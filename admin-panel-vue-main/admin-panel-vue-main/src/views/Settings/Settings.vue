<template>
  <div class="flex flex-col lg:flex-row gap-6 min-h-[calc(100vh-200px)]">
    <!-- Левая боковая панель -->
    <aside class="lg:w-64 flex-shrink-0">
      <div class="bg-white rounded-lg p-4 lg:p-6 shadow-sm border border-gray-100 sticky top-4">
        <h2 class="text-lg font-semibold text-gray-900 mb-4 hidden lg:block">Настройки</h2>
        
        <!-- Меню табов -->
        <nav class="space-y-1">
          <router-link
            v-for="tab in tabs"
            :key="tab.id"
            :to="tab.to"
            v-slot="{ isActive, navigate }"
          >
            <button
              @click="navigate"
              :class="[
                'w-full text-left px-4 py-3 rounded-lg transition-colors',
                isActive
                  ? 'bg-gray-100 text-gray-900 font-medium'
                  : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
              ]"
            >
              {{ tab.label }}
            </button>
          </router-link>
        </nav>
      </div>
    </aside>

    <!-- Основная область контента -->
    <main class="flex-1">
      <div class="bg-white rounded-lg p-6 sm:p-8 shadow-sm border border-gray-100">
        <router-view v-slot="{ Component }">
          <Transition name="fade-slide" mode="out-in">
            <component :is="Component" />
          </Transition>
        </router-view>
      </div>
    </main>

  </div>
</template>

<script setup>
const tabs = [
  { id: 'appearance', label: 'Внешний вид', to: '/settings/appearance' },
  { id: 'privacy', label: 'Конфиденциальность', to: '/settings/privacy' },
  { id: 'integrations', label: 'Интеграции', to: '/settings/integrations' },
  { id: 'payment', label: 'Оплата', to: '/settings/payment' },
  { id: 'notifications', label: 'Уведомления', to: '/settings/notifications' },
  { id: 'language', label: 'Язык', to: '/settings/language' },
  { id: 'hotkeys', label: 'Горячие клавиши', to: '/settings/hotkeys' },
  { id: 'additional', label: 'Дополнительно', to: '/settings/additional' }
]
</script>

<style scoped>
.fade-slide-enter-active,
.fade-slide-leave-active {
  transition: all 0.3s ease;
}

.fade-slide-enter-from {
  opacity: 0;
  transform: translateX(10px);
}

.fade-slide-leave-to {
  opacity: 0;
  transform: translateX(-10px);
}
</style>
