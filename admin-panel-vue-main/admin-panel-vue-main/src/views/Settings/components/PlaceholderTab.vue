<template>
  <div class="animate-fade-in">
    <h1 class="text-2xl sm:text-3xl font-bold text-gray-900 mb-6">{{ title }}</h1>
    <div class="text-center py-12">
      <p class="text-gray-500">Настройка {{ title.toLowerCase() }} в разработке</p>
    </div>
  </div>
</template>

<script setup>
defineProps({
  title: {
    type: String,
    required: true
  }
})
</script>

<style scoped>
.animate-fade-in {
  animation: fadeIn 0.3s ease-out;
}
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(8px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>
