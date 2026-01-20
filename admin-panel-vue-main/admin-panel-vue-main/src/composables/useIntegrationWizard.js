import { ref, reactive, computed } from 'vue'
import api from '../api/axios'
import { useToaster } from './useToaster'
import { useRouter } from 'vue-router'

// Global State (persists across page navigations within the SPA)
const currentStep = ref(1)
const lastIntegrationId = ref(null)
const error = ref(null)

const form = reactive({
  platform: 'YANDEX_DIRECT',
  client_id: null,
  client_name: '',
  account_id: null,
  agency_client_login: '',
  primary_goal_id: null,
  sync_depth: 90,
  auto_sync: true
})

const statsDateRange = ref('30')

const loadingStates = reactive({
  profiles: false,
  campaigns: false,
  goals: false,
  finish: false
})

const campaigns = ref([])
const selectedCampaignIds = ref([])
const allFromProfile = ref(false)

const goals = ref([])
const selectedGoalIds = ref([])
const allFromGoalsFromProfile = ref(false)

const profiles = ref([])

export function useIntegrationWizard() {
  const toaster = useToaster()
  const router = useRouter()

  const resetStore = () => {
    currentStep.value = 1
    lastIntegrationId.value = null
    error.value = null
    form.client_id = null
    form.client_name = ''
    form.account_id = null
    form.agency_client_login = ''
    form.primary_goal_id = null
    form.sync_depth = 90
    form.auto_sync = true
    statsDateRange.value = '30'
    campaigns.value = []
    selectedCampaignIds.value = []
    allFromProfile.value = false
    goals.value = []
    selectedGoalIds.value = []
    profiles.value = []
  }

  const getDateRangeParams = () => {
    const end = new Date()
    const start = new Date()
    start.setDate(end.getDate() - parseInt(statsDateRange.value))
    return {
      date_from: start.toISOString().split('T')[0],
      date_to: end.toISOString().split('T')[0]
    }
  }

  const fetchProfiles = async (integrationId) => {
    loadingStates.profiles = true
    try {
      const res = await api.get(`/integrations/${integrationId}/profiles`)
      profiles.value = res.data
    } catch (err) {
      error.value = "Ошибка при загрузке профилей"
    } finally {
      loadingStates.profiles = false
    }
  }

  const fetchCampaigns = async (integrationId) => {
    loadingStates.campaigns = true
    try {
      const { date_from, date_to } = getDateRangeParams()
      const res = await api.post(`/integrations/${integrationId}/discover-campaigns?date_from=${date_from}&date_to=${date_to}`)
      campaigns.value = res.data
      // Select active campaigns by default
      selectedCampaignIds.value = res.data.filter(c => c.state === 'ON' || c.is_active).map(c => c.id)
      
      // If none are active (newly discovered), select all
      if (selectedCampaignIds.value.length === 0) {
        selectedCampaignIds.value = res.data.map(c => c.id)
      }
    } catch (err) {
      error.value = "Ошибка при загрузке кампаний"
    } finally {
      loadingStates.campaigns = false
    }
  }

  const fetchGoals = async (integrationId) => {
    loadingStates.goals = true
    try {
      const { date_from, date_to } = getDateRangeParams()
      const res = await api.get(`/integrations/${integrationId}/goals?account_id=${form.account_id}&date_from=${date_from}&date_to=${date_to}`)
      goals.value = res.data

      // Auto-select primary goal if not set
      if (res.data.length > 0 && !form.primary_goal_id) {
        const bestGoal = [...res.data].sort((a, b) => (b.conversion_rate || 0) - (a.conversion_rate || 0))[0]
        if (bestGoal) {
          selectPrimaryGoal(bestGoal.id)
        }
      }
    } catch (err) {
      error.value = "Ошибка при загрузке целей"
    } finally {
      loadingStates.goals = false
    }
  }

  const fetchIntegration = async (id) => {
    try {
      const res = await api.get(`/integrations/${id}`)
      const integration = res.data
      form.platform = integration.platform
      form.client_id = integration.client_id
      form.account_id = integration.account_id
      form.agency_client_login = integration.account_id
      if (integration.client) form.client_name = integration.client.name
    } catch (err) {
      error.value = "Ошибка при загрузке данных интеграции"
    }
  }

  const toggleCampaignSelection = (id) => {
    const idx = selectedCampaignIds.value.indexOf(id)
    if (idx > -1) selectedCampaignIds.value.splice(idx, 1)
    else selectedCampaignIds.value.push(id)
    allFromProfile.value = false
  }

  const bulkSelectCampaigns = (ids) => {
    ids.forEach(id => {
      if (!selectedCampaignIds.value.includes(id)) {
        selectedCampaignIds.value.push(id)
      }
    })
  }

  const bulkDeselectCampaigns = (ids) => {
    selectedCampaignIds.value = selectedCampaignIds.value.filter(id => !ids.includes(id))
    allFromProfile.value = false
  }

  const bulkSelectGoals = (ids) => {
    ids.forEach(id => {
      if (!selectedGoalIds.value.includes(id)) {
        selectedGoalIds.value.push(id)
      }
    })
  }

  const bulkDeselectGoals = (ids) => {
    selectedGoalIds.value = selectedGoalIds.value.filter(id => !ids.includes(id))
  }

  const selectPrimaryGoal = (id) => {
    form.primary_goal_id = id
  }

  const finishConnection = async () => {
    loadingStates.finish = true
    try {
      // 1. Update campaign statuses in bulk (only selected are active)
      const campaignUpdates = campaigns.value.map(c => ({
        id: c.id,
        is_active: selectedCampaignIds.value.includes(c.id)
      }))
      
      const bulkUpdatePromise = api.put('campaigns/bulk-update', campaignUpdates)
      
      const integrationPromise = api.patch(`/integrations/${lastIntegrationId.value}`, {
        selected_goals: [...selectedGoalIds.value],
        primary_goal_id: form.primary_goal_id,
        auto_sync: form.auto_sync,
        sync_interval: 1440 // Daily
      })
      
      await Promise.all([bulkUpdatePromise, integrationPromise])
      
      // 3. Trigger initial sync automatically (sync_depth days)
      try {
        await api.post(`/integrations/${lastIntegrationId.value}/sync`, { days: form.sync_depth })
      } catch (syncErr) {
        console.warn('Initial sync failed, but integration was saved:', syncErr)
      }

      toaster.success("Интеграция успешно настроена!")
      resetStore()
      if (router) router.push('/settings')
    } catch (err) {
      error.value = "Ошибка при завершении настройки"
    } finally {
      loadingStates.finish = false
    }
  }

  return {
    // State
    currentStep,
    lastIntegrationId,
    error,
    form,
    loadingStates,
    campaigns,
    selectedCampaignIds,
    allFromProfile,
    goals,
    selectedGoalIds,
    allFromGoalsFromProfile,
    profiles,
    statsDateRange,

    // Actions
    resetStore,
    fetchProfiles,
    fetchCampaigns,
    fetchGoals,
    fetchIntegration,
    finishConnection,
    toggleCampaignSelection,
    bulkSelectCampaigns,
    bulkDeselectCampaigns,
    bulkSelectGoals,
    bulkDeselectGoals,
    selectPrimaryGoal
  }
}
