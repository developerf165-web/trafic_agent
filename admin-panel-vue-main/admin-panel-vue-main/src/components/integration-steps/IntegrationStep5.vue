<template>
  <div class="space-y-8 py-2">
    <!-- Header -->
    <div class="text-center space-y-2">
      <div class="inline-flex items-center justify-center w-16 h-16 bg-blue-50 rounded-full mb-2">
        <ClipboardDocumentCheckIcon class="w-8 h-8 text-blue-600" />
      </div>
      <h2 class="text-xl font-black text-gray-900 uppercase tracking-tight">Просмотр настроек</h2>
      <p class="text-[13px] text-gray-500 font-bold max-w-sm mx-auto">
        Пожалуйста, проверьте выбранные параметры перед окончательным подключением интеграции.
      </p>
    </div>

    <div class="max-w-2xl mx-auto">
      <div class="bg-white border border-gray-100 rounded-[3rem] overflow-hidden shadow-[0_30px_80px_-15px_rgba(0,0,0,0.08)]">
        <!-- Card Header -->
        <div class="bg-gradient-to-r from-gray-900 to-blue-900 p-10 text-white relative overflow-hidden">
          <div class="absolute right-0 top-0 w-64 h-64 bg-white/5 rounded-full -translate-y-1/2 translate-x-1/2 blur-3xl"></div>
          <div class="relative z-10 flex items-center justify-between">
            <div class="space-y-2">
              <p class="text-[10px] font-black text-blue-300 uppercase tracking-[0.3em]">КОНФИГУРАЦИЯ ЗАВЕРШЕНА</p>
              <h3 class="text-3xl font-black tracking-tight">{{ projectName }}</h3>
            </div>
            <div class="w-16 h-16 bg-white/10 backdrop-blur-md rounded-2xl flex items-center justify-center border border-white/20">
               <PlatformIcon :platform="platform || 'YANDEX_DIRECT'" size="lg" class="brightness-0 invert opacity-80" />
            </div>
          </div>
        </div>

        <div class="p-10 space-y-10">
          <!-- Main Details -->
          <div class="grid grid-cols-2 gap-12">
            <div class="space-y-2">
               <p class="text-[9px] font-black text-gray-400 uppercase tracking-[0.2em]">Аккаунт</p>
               <div class="flex items-center gap-3">
                 <div class="w-8 h-8 rounded-full bg-blue-50 flex items-center justify-center">
                   <UserCircleIcon class="w-5 h-5 text-blue-600" />
                 </div>
                 <div class="flex flex-col">
                   <span class="text-[14px] font-black text-gray-800 leading-none">{{ selectedProfileName }}</span>
                   <span class="text-[11px] font-bold text-gray-400 mt-1">{{ selectedProfileLogin }}</span>
                 </div>
               </div>
            </div>
            <div class="space-y-2">
               <p class="text-[9px] font-black text-gray-400 uppercase tracking-[0.2em]">Валюта</p>
               <div class="flex items-center gap-3">
                  <div class="w-8 h-8 rounded-full bg-emerald-50 flex items-center justify-center">
                    <span class="text-[12px] font-black text-emerald-600">$</span>
                  </div>
                  <span class="text-[14px] font-black text-gray-800 uppercase">{{ currency || 'RUB' }}</span>
               </div>
            </div>
          </div>

          <!-- Campaigns & Goals -->
          <div class="space-y-6">
             <div class="flex items-center justify-between py-4 border-y border-gray-50">
                <div class="flex items-center gap-3">
                   <MegaphoneIcon class="w-5 h-5 text-gray-400" />
                   <span class="text-[13px] font-black text-gray-700 uppercase tracking-tight">Выбрано кампаний</span>
                </div>
                <span class="px-3 py-1 bg-black text-white rounded-lg text-[12px] font-black">{{ selectedCampaignsCount }}</span>
             </div>

             <div class="space-y-4">
                <div class="flex items-center gap-3">
                   <StarIcon class="w-5 h-5 text-yellow-400" />
                   <span class="text-[13px] font-black text-gray-400 uppercase tracking-tight">Основная цель</span>
                </div>
                <div class="p-5 bg-blue-50/50 rounded-2xl border border-blue-100 flex items-center justify-between">
                   <span class="text-[15px] font-black text-blue-900 tracking-tight">{{ primaryGoalName || 'Не выбрана' }}</span>
                   <div class="px-3 py-1 bg-blue-600 text-white rounded-md text-[9px] font-black uppercase">Primary</div>
                </div>
             </div>
          </div>

          <!-- Extra Settings -->
          <div class="flex items-center justify-between gap-4 p-6 bg-gray-50 rounded-[2rem]">
             <div class="flex items-center gap-3">
                <ArrowPathRoundedSquareIcon class="w-5 h-5 text-gray-400" />
                <span class="text-[12px] font-black text-gray-600 uppercase tracking-tight">Синхронизация: {{ syncDepth }}дн / Авто</span>
             </div>
             <div class="flex items-center gap-2">
                <div class="w-2 h-2 rounded-full bg-green-500 animate-pulse"></div>
                <span class="text-[10px] font-black text-green-600 uppercase tracking-widest">Готов к деплою</span>
             </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Final Checkbox & Settings -->
    <div class="bg-blue-600 rounded-[2rem] p-8 text-white shadow-xl relative overflow-hidden group">
      <!-- Decorative circles -->
      <div class="absolute -top-12 -right-12 w-48 h-48 bg-white/10 rounded-full transition-transform group-hover:scale-110"></div>
      <div class="absolute -bottom-8 -left-8 w-24 h-24 bg-white/10 rounded-full transition-transform group-hover:scale-125"></div>
      
      <div class="relative z-10 flex flex-col md:flex-row items-center justify-between gap-6">
        <div class="space-y-4">
          <div class="flex items-center gap-4">
             <div class="w-12 h-12 bg-white/20 rounded-2xl flex items-center justify-center backdrop-blur-sm">
                <ArrowPathRoundedSquareIcon class="w-6 h-6 text-white" />
             </div>
             <div>
               <p class="text-[10px] font-black text-blue-100 uppercase tracking-widest leading-none mb-1">Глубина и Автосинхрон</p>
               <h3 class="text-[17px] font-black">Синхронизация за {{ syncDepth }} дней</h3>
             </div>
          </div>
          <div class="flex items-center gap-3">
            <div 
              class="w-10 h-5 bg-white/20 rounded-full p-1 cursor-not-allowed flex shadow-inner"
              :class="autoSync ? 'opacity-100' : 'opacity-40'"
            >
              <div class="w-3 h-3 bg-white rounded-full shadow-md" :class="autoSync ? 'ml-auto' : ''"></div>
            </div>
            <span class="text-[12px] font-black uppercase tracking-wider text-blue-50">Автоматическая синхронизация включена</span>
          </div>
        </div>
        
        <div class="text-center md:text-right">
          <p class="text-[10px] font-black text-blue-100 uppercase tracking-widest mb-2">Нажмите кнопку ниже для старта</p>
          <div class="flex items-center gap-2 justify-center md:justify-end">
            <SparklesIcon class="w-5 h-5 text-yellow-300 animate-pulse" />
            <span class="text-lg font-black italic">Готовность 100%</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { 
  ClipboardDocumentCheckIcon, 
  BuildingOfficeIcon,
  MegaphoneIcon,
  UserCircleIcon,
  PresentationChartLineIcon,
  StarIcon,
  SparklesIcon,
  ArrowPathRoundedSquareIcon
} from '@heroicons/vue/24/solid'
import { CheckIcon } from '@heroicons/vue/24/outline'

const props = defineProps({
  projectName: String,
  platform: String,
  selectedProfileName: String,
  selectedProfileLogin: String,
  currency: String,
  selectedCampaignsList: {
    type: Array,
    default: () => []
  },
  primaryGoalName: String,
  secondaryGoalsList: {
    type: Array,
    default: () => []
  },
  syncDepth: [Number, String],
  autoSync: Boolean
})

const selectedCampaignsCount = computed(() => props.selectedCampaignsList.length)
</script>

<style scoped>
.custom-scrollbar::-webkit-scrollbar {
  width: 4px;
}
.custom-scrollbar::-webkit-scrollbar-track {
  background: transparent;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background: #e5e7eb;
  border-radius: 10px;
}
.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background: #d1d5db;
}
</style>
