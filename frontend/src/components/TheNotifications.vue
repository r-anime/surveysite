<template>
  <div class="toast-container position-fixed bottom-0 start-50 translate-middle-x mb-4" style="z-index:100000;"> <!-- Notifications ALWAYS have to be on top -->
    <div v-for="(notification, idx) in notifications" :key="idx" class="toast align-items-center text-white border-0" :class="`bg-${notification.color}`" :id="`toast${idx}`" role="alert" aria-live="assertive" aria-atomic="true">
      <div class="d-flex">
        <div class="toast-body">
          {{ notification.message }}
        </div>
        <button type="button" class="btn-close btn-close-white me-2 m-auto" aria-label="Close" data-bs-dismiss="toast"></button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import NotificatonService, { type Notification } from '@/util/notification-service';
import { Toast } from 'bootstrap';
import { nextTick, ref } from 'vue';

const notifications = ref<Notification[]>([]);


NotificatonService.subscribe(addNotification);


function addNotification(notification: Notification): void {
  const idx = notifications.value.length;
  notifications.value.push(notification);

  nextTick(() => {
    const toast = new Toast(`#toast${idx}`, {
      autohide: true,
      delay: 5000,
    });
    toast.show();
  });
}
</script>
