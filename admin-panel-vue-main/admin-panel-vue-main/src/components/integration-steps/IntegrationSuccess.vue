<template>
  <div class="flex flex-col items-center justify-center py-12 text-center space-y-8 animate-fade-in">
    <!-- Success Animation -->
    <div class="relative">
      <div class="absolute inset-0 bg-green-100 rounded-full scale-150 blur-2xl opacity-50 animate-pulse"></div>
      <div class="relative w-24 h-24 bg-green-500 rounded-full flex items-center justify-center shadow-[0_0_50px_rgba(34,197,94,0.4)] animate-bounce-subtle">
        <CheckIcon class="w-12 h-12 text-white" stroke-width="4" />
      </div>
    </div>

    <div class="space-y-3">
      <h2 class="text-3xl font-black text-gray-900 uppercase tracking-tighter">Поздравляем!</h2>
      <p class="text-gray-500 font-bold max-w-sm mx-auto">
        Интеграция для проекта <span class="text-blue-600 font-black">{{ projectName }}</span> успешно настроена и запущена.
      </p>
    </div>

    <!-- Mini Summary Card -->
    <div class="bg-gray-50/50 border border-gray-100 rounded-[2.5rem] p-8 w-full max-w-lg shadow-inner">
      <div class="grid grid-cols-2 gap-6">
        <div class="text-left space-y-1">
          <p class="text-[9px] font-black text-gray-400 uppercase tracking-[0.2em]">Платформа</p>
          <div class="flex items-center gap-2">
            <PlatformIcon :platform="platform" size="xs" />
            <span class="text-[14px] font-black text-gray-800">{{ platform === 'YANDEX_DIRECT' ? 'Яндекс Директ' : 'VK Ads' }}</span>
          </div>
        </div>
        <div class="text-left space-y-1">
          <p class="text-[9px] font-black text-gray-400 uppercase tracking-[0.2em]">Статус</p>
          <div class="flex items-center gap-2">
            <div class="w-2 h-2 bg-green-500 rounded-full animate-ping"></div>
            <span class="text-[14px] font-black text-green-600 uppercase">Активно</span>
          </div>
        </div>
      </div>
    </div>

    <div class="pt-4 flex flex-col items-center gap-4">
       <p class="text-[11px] text-gray-400 font-bold">Синхронизация данных уже началась и займет несколько минут.</p>
    </div>
  </div>
</template>

<script setup>
import { CheckIcon } from '@heroicons/vue/24/outline'
import PlatformIcon from '../ui/PlatformIcon.vue'

defineProps({
  projectName: String,
  platform: String
})
</script>

<style scoped>
.animate-fade-in {
  animation: fadeIn 0.8s cubic-bezier(0.4, 0, 0.2, 1);
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

@keyframes bounce-subtle {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-10px); }
}

.animate-bounce-subtle {
  animation: bounce-subtle 2s infinite ease-in-out;
}
</style>
