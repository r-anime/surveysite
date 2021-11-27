<template>
  <div class="toast-container mb-4">
    <div v-for="(notification, idx) in notifications" :key="idx" class="toast align-items-center text-white border-0" :class="`bg-${notification.color}`" :id="`toast-${idx}`" role="alert" aria-live="assertive" aria-atomic="true">
      <div class="d-flex">
        <div class="toast-body">
          {{ notification.message }}
        </div>
        <button type="button" class="btn-close btn-close-white me-2 m-auto" aria-label="Close" data-bs-dismiss="toast"></button>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { Options, Vue } from 'vue-class-component';
import NotificatonService, { Notification } from '@/util/notification-service';
import { Toast } from 'bootstrap';

@Options({})
export default class TheNavbar extends Vue {
  notifications: Notification[] = [];

  created(): void {
    NotificatonService.subscribe(this.addNotification);
  }

  addNotification(notification: Notification): void {
    const idx = this.notifications.length;
    this.notifications.push(notification);

    this.$nextTick(() => {
      const toast = new Toast(`#toast-${idx}`, {
        autohide: true,
        delay: 5000,
      });
      toast.show();
    });
  }
}
</script>
