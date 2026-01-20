<template>
  <div class="space-y-6">
    <!-- Header & Search -->
    <div class="flex flex-col md:flex-row md:items-center justify-between gap-4">
      <label class="block text-[9px] font-black text-gray-400 uppercase tracking-[0.2em] px-1">ВЫБЕРИТЕ ПРОФИЛЬ ДЛЯ ИНТЕГРАЦИИ</label>
      
      <div v-if="profiles.length > 5 || searchQuery" class="relative group w-full md:w-64">
        <div class="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
          <MagnifyingGlassIcon class="h-4 w-4 text-gray-400 group-focus-within:text-blue-500 transition-colors" />
        </div>
        <input 
          type="text" 
          v-model="searchQuery"
          placeholder="Поиск аккаунта..."
          class="block w-full pl-11 pr-10 py-3 bg-white border border-gray-100 rounded-2xl text-[12px] font-bold text-gray-900 placeholder-gray-400 focus:ring-4 focus:ring-blue-500/10 focus:border-blue-500 transition-all shadow-sm"
        >
        <button 
          v-if="searchQuery"
          @click="searchQuery = ''"
          class="absolute inset-y-0 right-0 pr-4 flex items-center text-gray-400 hover:text-gray-600 transition-colors"
        >
          <XMarkIcon class="h-4 w-4" />
        </button>
      </div>
    </div>

    <!-- Profile Power Table -->
    <div class="bg-white border border-gray-100 rounded-[2rem] overflow-hidden shadow-sm">
      <table class="w-full text-left border-collapse">
        <thead>
          <tr class="bg-gray-50/50 border-b border-gray-100">
            <th class="w-12 px-5 py-4 text-center">
              <CheckIcon class="w-4 h-4 mx-auto text-gray-300" />
            </th>
            <th class="px-4 py-4 text-[10px] font-black text-gray-400 uppercase tracking-widest leading-tight">Тип аккаунта</th>
            <th class="px-4 py-4 text-[10px] font-black text-gray-400 uppercase tracking-widest leading-tight">Профиль / Логин</th>
            <th class="px-4 py-4 text-[10px] font-black text-gray-400 uppercase tracking-widest leading-tight">Валюта / Баланс</th>
            <th class="px-3 py-4 text-[10px] font-black text-gray-400 uppercase tracking-widest leading-tight text-right">Кампаний</th>
            <th class="px-3 py-4 text-[10px] font-black text-gray-400 uppercase tracking-widest leading-tight text-right">Расход/мес</th>
          </tr>
        </thead>
        <tbody>
          <!-- Loading State -->
          <template v-if="loading">
            <tr v-for="i in 4" :key="i" class="border-b border-gray-50">
              <td class="px-5 py-5 text-center"><Skeleton width="5" height="5" rounded="md" class="mx-auto" /></td>
              <td class="px-4 py-5"><Skeleton width="20" height="3" /></td>
              <td class="px-4 py-5"><Skeleton width="48" height="4" /></td>
              <td class="px-4 py-5"><Skeleton width="24" height="4" /></td>
              <td class="px-3 py-5"><Skeleton width="10" height="3" class="ml-auto" /></td>
              <td class="px-3 py-5"><Skeleton width="16" height="3" class="ml-auto" /></td>
            </tr>
          </template>

          <template v-else>
            <tr 
              v-for="profile in filteredProfiles" 
              :key="profile.login"
              @click="selectProfile(profile)"
              class="border-b border-gray-50 last:border-none group hover:bg-blue-50/50 hover:pl-2 transition-all cursor-pointer"
              :class="{ 'bg-blue-50/50 shadow-inner': selectedAccountId === profile.login }"
            >
              <!-- Selection -->
              <td class="px-5 py-4 text-center">
                <div 
                  class="w-5 h-5 mx-auto rounded-md border-2 flex items-center justify-center transition-all bg-white" 
                  :class="selectedAccountId === profile.login ? 'bg-blue-600 border-blue-600' : 'border-gray-200 group-hover:border-gray-400'"
                >
                  <CheckIcon v-if="selectedAccountId === profile.login" class="w-3.5 h-3.5 text-white" stroke-width="4" />
                </div>
              </td>

              <!-- Type -->
              <td class="px-4 py-4">
                <span 
                  class="px-2.5 py-1 rounded-full text-[8px] font-black uppercase tracking-widest border"
                  :class="[
                    profile.type === 'personal' ? 'bg-orange-50/50 text-orange-600 border-orange-100' : 
                    profile.type === 'agency_client' ? 'bg-blue-50/50 text-blue-600 border-blue-100' :
                    'bg-gray-50 text-gray-500 border-gray-100'
                  ]"
                >
                  {{ 
                    profile.type === 'personal' ? 'Личный' : 
                    profile.type === 'agency_client' ? 'Клиент агентства' : 
                    profile.type === 'managed' ? 'Редактор' : 'Аккаунт'
                  }}
                </span>
              </td>

              <!-- Name / Login -->
              <td class="px-4 py-4">
                <div class="flex flex-col">
                  <span class="text-[13px] font-black text-gray-800 leading-tight group-hover:text-blue-600 transition-colors">
                    {{ profile.name || profile.login }}
                  </span>
                  <span class="text-[9px] text-gray-400 font-bold uppercase tracking-wider mt-0.5">
                    {{ profile.login }}
                  </span>
                </div>
              </td>

              <!-- Currency / Balance -->
              <td class="px-4 py-4">
                <div v-if="profile.currency" class="inline-flex items-center gap-1.5 px-2.5 py-1 bg-green-50 rounded-full border border-green-100/50">
                  <span class="text-[9px] font-black text-green-600 uppercase tracking-wider">{{ profile.currency }}</span>
                  <span v-if="profile.balance !== undefined" class="text-[10px] font-black text-green-700">
                    {{ formatMoney(profile.balance, profile.currency) }}
                  </span>
                </div>
                <span v-else class="text-gray-300 text-[10px] font-black">—</span>
              </td>

              <!-- Campaigns Count -->
              <td class="px-3 py-4 text-right">
                <div v-if="profile.campaigns_count !== undefined" class="flex flex-col items-end">
                  <span class="text-[12px] font-black text-gray-700">{{ profile.campaigns_count }}</span>
                  <span v-if="profile.active_campaigns" class="text-[8px] text-green-600 font-bold uppercase tracking-tighter">
                    {{ profile.active_campaigns }} активных
                  </span>
                </div>
                <span v-else class="text-gray-300 text-[10px] font-black">—</span>
              </td>

              <!-- Monthly Spend -->
              <td class="px-3 py-4 text-right">
                <span v-if="profile.monthly_spend !== undefined" class="text-[12px] font-black text-gray-900">
                  {{ formatMoney(profile.monthly_spend, profile.currency) }}
                </span>
                <span v-else class="text-gray-300 text-[10px] font-black">—</span>
              </td>
            </tr>

            <!-- Empty Result -->
            <tr v-if="filteredProfiles.length === 0">
              <td colspan="6" class="py-20 text-center">
                <div class="w-16 h-16 bg-gray-50 rounded-full flex items-center justify-center mx-auto mb-4">
                  <MagnifyingGlassIcon class="w-8 h-8 text-gray-200" />
                </div>
                <p class="text-[12px] font-black text-gray-400 uppercase tracking-widest">Профили не найдены</p>
                <p class="text-[10px] text-gray-400 mt-2">Попробуйте изменить запрос поиска</p>
              </td>
            </tr>
          </template>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { MagnifyingGlassIcon, XMarkIcon } from '@heroicons/vue/20/solid'
import { CheckIcon } from '@heroicons/vue/24/outline'
import Skeleton from '../ui/Skeleton.vue'

const props = defineProps({
  profiles: Array,
  selectedAccountId: String,
  loading: Boolean,
  platform: String
})

const emit = defineEmits(['selectProfile', 'next'])

const searchQuery = ref('')

const formatMoney = (val, currency = 'RUB') => {
  try {
    return new Intl.NumberFormat('ru-RU', { 
      style: 'currency', 
      currency: currency === 'RUB' ? 'RUB' : (currency || 'RUB'), 
      maximumFractionDigits: 0 
    }).format(val)
  } catch (e) {
    return `${val} ${currency}`
  }
}

const filteredProfiles = computed(() => {
  if (!props.profiles) return []
  if (!searchQuery.value) return props.profiles
  const q = searchQuery.value.toLowerCase()
  return props.profiles.filter(p => 
    (p.name && p.name.toLowerCase().includes(q)) || 
    (p.login && p.login.toLowerCase().includes(q))
  )
})

const selectProfile = (profile) => {
  emit('selectProfile', profile)
}
</script>
