<template>
  <div class="toast-container">
    <div v-for="(notification, idx) in notifications" :key="idx" class="toast show align-items-center text-white border-0" :class="`bg-${notification.color} toast-${idx}`" role="alert" aria-live="assertive" aria-atomic="true">
      <div class="d-flex">
        <div class="toast-body">
          {{ notification.message }}
        </div>
        <button type="button" class="btn-close btn-close-white me-2 m-auto" aria-label="Close" @click="removeNotification(idx)"></button>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { Options, Vue } from 'vue-class-component';
import NotificatonService, { Notification } from '@/util/notification-service';

@Options({
  data() {
    return {
      notifications: [] as Notification[],
    }
  },
  methods: {
    addNotification(notification: Notification) {
      this.notifications.push(notification);
    },
    removeNotification(idx: number) {
      this.notifications.splice(idx, 1);
    },
  },
  async mounted() {
    NotificatonService.subscribe(this.addNotification);
  }
})
export default class TheNavbar extends Vue {}
</script>
