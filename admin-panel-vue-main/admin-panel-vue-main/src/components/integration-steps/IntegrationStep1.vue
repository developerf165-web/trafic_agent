<template>
  <div class="pr-1 pb-4 space-y-6">
    <div v-if="error" class="p-4 bg-red-50 border border-red-100 text-red-600 text-[12px] rounded-xl flex items-start gap-3 animate-shake shadow-sm">
      <svg class="w-5 h-5 flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clip-rule="evenodd"></path></svg>
      <span class="font-bold">{{ error }}</span>
    </div>

    <form @submit.prevent="$emit('next')" class="space-y-6">
      <!-- Platform Info & Health (Enriched) -->
      <div class="bg-gradient-to-br from-blue-600 to-indigo-700 rounded-[2.5rem] p-8 text-white shadow-2xl relative overflow-hidden group mb-10">
        <div class="absolute -right-20 -bottom-20 w-80 h-80 bg-white/10 rounded-full blur-3xl group-hover:scale-110 transition-transform duration-1000"></div>
        <div class="relative z-10 flex items-center gap-8">
          <div class="w-20 h-20 bg-white/20 backdrop-blur-xl rounded-[2rem] flex items-center justify-center border border-white/30 shadow-2xl">
             <PlatformIcon :platform="modelValue.platform" class="w-12 h-12 brightness-0 invert" />
          </div>
          <div class="flex-grow">
            <h2 class="text-2xl font-black mb-2 tracking-tight uppercase">Настройка {{ PLATFORMS[modelValue.platform]?.label }}</h2>
            <p class="text-blue-100 text-[13px] font-bold max-w-lg leading-relaxed opacity-90">
              {{ isCreatingNewProject ? 'Создайте новый проект для отслеживания данных' : 'Выберите существующий проект или создайте новый для начала работы' }}
            </p>
          </div>
        </div>
      </div>

      <!-- Platform Selection Grid -->
      <div class="space-y-4">
        <label class="block text-[9px] font-black text-gray-400 uppercase tracking-[0.2em] mb-3 px-1">ВЫБЕРИТЕ РЕКЛАМНЫЙ КАНАЛ</label>
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3">
          <div 
            v-for="(config, key) in PLATFORMS" 
            :key="key"
            @click="!config.comingSoon && updateForm({ platform: key })"
            class="relative group p-3 bg-white border-2 rounded-2xl transition-all duration-300 cursor-pointer overflow-hidden"
            :class="[
              modelValue.platform === key ? 'border-blue-600 ring-4 ring-blue-50 shadow-md' : 'border-gray-50 opacity-60 hover:opacity-100 hover:border-blue-200',
              config.comingSoon ? 'opacity-30 cursor-not-allowed filter grayscale pointer-events-none' : ''
            ]"
          >
            <div class="flex items-center gap-3">
              <div 
                class="w-10 h-10 rounded-xl flex items-center justify-center text-[11px] font-black transition-all group-hover:scale-105"
                :class="config.className"
              >
                {{ config.initials }}
              </div>
              <div class="flex flex-col">
                <h3 class="text-[11px] font-black text-black uppercase tracking-tight leading-none mb-1">{{ config.label }}</h3>
                <span class="text-[8px] font-bold text-gray-400 uppercase tracking-tighter">{{ config.comingSoon ? 'Скоро' : 'Доступно' }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-6 pt-4">
        <!-- Project Selection & Creation -->
        <div class="space-y-4">
          <label class="block text-[9px] font-black text-gray-400 uppercase tracking-[0.2em] mb-3 px-1">ВЫБЕРИТЕ ПРОЕКТ (КЛИЕНТА)</label>
          
          <div class="relative">
            <div class="relative group">
              <div class="absolute inset-y-0 left-0 pl-5 flex items-center pointer-events-none">
                <MagnifyingGlassIcon class="h-5 w-5 text-gray-400 group-focus-within:text-blue-500 transition-colors" />
              </div>
              <input 
                type="text"
                :value="projectSearchQuery"
                @input="handleSearchInput"
                @focus="isDropdownOpen = true"
                placeholder="Поиск проекта..."
                class="w-full pl-14 pr-12 py-5 bg-white border-2 border-gray-100 rounded-[1.5rem] focus:ring-8 focus:ring-blue-500/5 focus:border-blue-500 transition-all font-black text-[15px] text-gray-900 shadow-sm placeholder:text-gray-300"
              >
              <div class="absolute inset-y-0 right-0 pr-3 flex items-center gap-1">
                <button 
                  v-if="projectSearchQuery"
                  type="button"
                  @click="clearProjectSearch"
                  class="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-xl transition-all"
                >
                  <XMarkIcon class="h-5 w-5" />
                </button>
                <button 
                  type="button"
                  @click.stop="isDropdownOpen = !isDropdownOpen"
                  class="p-2 hover:bg-gray-100 rounded-xl transition-colors"
                >
                  <ChevronDownIcon class="h-6 w-6 text-gray-400" :class="{ 'rotate-180': isDropdownOpen }" />
                </button>
              </div>
            </div>

            <Transition name="fade-scale">
              <div 
                v-if="isDropdownOpen" 
                class="absolute z-[60] left-0 right-0 mt-3 bg-white border border-gray-100 rounded-[2rem] shadow-[0_30px_70px_rgba(0,0,0,0.15)] overflow-hidden animate-modal-in backdrop-blur-xl"
                v-click-outside="() => isDropdownOpen = false"
              >
                <div class="max-h-[350px] overflow-y-auto py-3 custom-scrollbar">
                  <div 
                    @click="handleCreateNewAction"
                    class="px-5 py-4 mx-3 mb-2 rounded-2xl flex items-center gap-4 cursor-pointer transition-all hover:bg-blue-600 group border border-transparent"
                  >
                    <div class="w-10 h-10 rounded-xl bg-blue-50 flex items-center justify-center group-hover:bg-white/20 transition-colors shadow-sm">
                      <PlusIcon class="w-5 h-5 text-blue-600 group-hover:text-white" />
                    </div>
                    <div>
                      <span class="block text-[13px] font-black text-blue-600 group-hover:text-white uppercase tracking-tight">СОЗДАТЬ НОВЫЙ ПРОЕКТ</span>
                    </div>
                  </div>
                  <div class="h-px bg-gray-100/50 mx-5 my-2"></div>
                  <div 
                    v-for="project in filteredProjects" 
                    :key="project.id"
                    @click="selectProject(project)"
                    class="px-5 py-4 mx-3 rounded-2xl flex items-center justify-between cursor-pointer transition-all hover:bg-gray-50 group mb-1 last:mb-0"
                    :class="{ 'bg-blue-50 text-blue-600': modelValue.client_id === project.id }"
                  >
                    <div class="flex items-center gap-4">
                      <div class="w-10 h-10 rounded-xl bg-gray-100 flex items-center justify-center text-[11px] font-black text-gray-500 group-hover:bg-white group-hover:text-blue-600 transition-colors shadow-sm">
                        {{ project.name.substring(0, 2).toUpperCase() }}
                      </div>
                      <span class="text-[14px] font-black text-gray-800 group-hover:text-blue-600 transition-colors">{{ project.name }}</span>
                    </div>
                    <CheckIcon v-if="modelValue.client_id === project.id" class="w-5 h-5 text-blue-600" />
                  </div>
                </div>
              </div>
            </Transition>
          </div>

          <div v-if="isCreatingNewProject" class="pt-4 animate-fade-in">
            <Input
              :modelValue="modelValue.client_name"
              @update:modelValue="updateForm({ client_name: $event })"
              label="НАЗВАНИЕ НОВОГО ПРОЕКТА"
              labelClass="text-[10px] font-black text-gray-400 uppercase tracking-[0.2em] mb-4 px-1"
              inputClass="rounded-[1.5rem] py-5 font-black text-black shadow-sm border-gray-100 focus:border-blue-500 bg-white"
              placeholder="Например: Мой Магазин"
              required
            />
          </div>
        </div>

        <!-- Sync Settings -->
        <div class="space-y-4">
          <label class="block text-[9px] font-black text-gray-400 uppercase tracking-[0.2em] mb-3 px-1">ПАРАМЕТРЫ СИНХРОНИЗАЦИИ</label>
          <div class="bg-gray-50/50 border border-gray-100 rounded-[2rem] p-6 space-y-5">
            <div class="flex items-center justify-between">
              <div class="flex flex-col">
                <span class="text-[12px] font-black text-gray-800 tracking-tight leading-none mb-1">Глубина истории</span>
                <span class="text-[9px] text-gray-400 font-bold uppercase tracking-wider">Начальный импорт</span>
              </div>
              <select 
                :value="modelValue.sync_depth || 90"
                @change="updateForm({ sync_depth: parseInt($event.target.value) })"
                class="bg-white border border-gray-100 rounded-xl px-3 py-2 text-[11px] font-black text-blue-600 focus:ring-4 focus:ring-blue-500/10 focus:border-blue-500 outline-none shadow-sm cursor-pointer"
              >
                <option :value="30">30 дней</option>
                <option :value="90">3 месяца</option>
                <option :value="180">6 месяцев</option>
                <option :value="365">1 год</option>
              </select>
            </div>

            <div class="flex items-center justify-between pt-4 border-t border-gray-200/50">
              <div class="flex flex-col">
                <span class="text-[12px] font-black text-gray-800 tracking-tight leading-none mb-1">Авто-синхронизация</span>
                <span class="text-[9px] text-gray-400 font-bold uppercase tracking-wider">Ежедневное обновление</span>
              </div>
              <button 
                type="button"
                @click="updateForm({ auto_sync: !modelValue.auto_sync })"
                class="w-11 h-6 rounded-full transition-all relative outline-none"
                :class="modelValue.auto_sync ? 'bg-blue-600 shadow-[0_4px_12px_rgba(37,99,235,0.3)]' : 'bg-gray-200'"
              >
                <div class="absolute top-1 left-1 w-4 h-4 bg-white rounded-full transition-all shadow-sm" :class="{ 'translate-x-5': modelValue.auto_sync }"></div>
              </button>
            </div>
          </div>
        </div>
      </div>

    </form>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { ChevronDownIcon, MagnifyingGlassIcon, XMarkIcon } from '@heroicons/vue/20/solid'
import { CheckIcon, PlusIcon } from '@heroicons/vue/24/outline'
import { PLATFORMS } from '../../constants/platformConfig'
import Input from '../../views/Settings/components/Input.vue'
import PlatformIcon from '../ui/PlatformIcon.vue'

const props = defineProps({
  modelValue: Object,
  projects: Array,
  isCreatingNewProject: Boolean,
  error: String,
  showToken: Boolean
})

const emit = defineEmits(['update:modelValue', 'update:isCreatingNewProject', 'next', 'openProjectSelector', 'openPlatformSelector'])

const vClickOutside = {
  mounted(el, binding) {
    el.clickOutsideEvent = (event) => {
      if (!(el === event.target || el.contains(event.target))) {
        binding.value(event)
      }
    }
    document.addEventListener('click', el.clickOutsideEvent)
  },
  unmounted(el) {
    document.removeEventListener('click', el.clickOutsideEvent)
  }
}

const projectSearchQuery = ref(props.modelValue.client_name || '')
const isDropdownOpen = ref(false)

const handleSearchInput = (e) => {
  projectSearchQuery.value = e.target.value
  isDropdownOpen.value = true
}

const filteredProjects = computed(() => {
  if (!projectSearchQuery.value) return props.projects
  const q = projectSearchQuery.value.toLowerCase()
  return props.projects.filter(p => p.name.toLowerCase().includes(q))
})

const selectProject = (project) => {
  emit('update:isCreatingNewProject', false)
  updateForm({ client_id: project.id, client_name: project.name })
  projectSearchQuery.value = project.name
  isDropdownOpen.value = false
}

const handleCreateNewAction = () => {
  emit('update:isCreatingNewProject', true)
  updateForm({ client_id: null, client_name: '' })
  projectSearchQuery.value = ''
  isDropdownOpen.value = false
}

const clearProjectSearch = () => {
  projectSearchQuery.value = ''
  updateForm({ client_id: null, client_name: '' })
}

const updateForm = (updates) => {
  emit('update:modelValue', { ...props.modelValue, ...updates })
}
</script>
