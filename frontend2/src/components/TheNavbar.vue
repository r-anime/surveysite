<template>
  <nav class="navbar navbar-expand-md bg-light sticky-top navbar-light">
    <div class="container-fluid">
      <router-link to="/" class="navbar-brand">/r/anime Surveys</router-link>

      <button class="navbar-toggler"
              type="button"
              data-bs-toggle="collapse"
              data-bs-target="#navbarNav"
              aria-controls="navbarNav"
              aria-expanded="false"
              aria-label="Toggle navigation">
        <span class="navbar-toggler-icon"></span>
      </button>

      <div v-if="userData" class="collapse navbar-collapse" id="navbarNav">
        <div class="navbar-nav ms-auto">
          <template v-if="userData.authenticated">
            <div class="navbar-text me-3 my-2 my-md-0">
              Logged in as
              <img v-if="userData.profilePictureUrl" class="mx-1 my-n3 align-middle rounded border" style="width:auto;height:35px;" :src="userData.profilePictureUrl">
              <svg v-else xmlns="http://www.w3.org/2000/svg" width="25" height="25" fill="currentColor" class="bi mx-1 my-n2" viewBox="0 0 16 16">
                <path d="M11 6a3 3 0 1 1-6 0 3 3 0 0 1 6 0z"/>
                <path d="M2 0a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V2a2 2 0 0 0-2-2H2zm12 1a1 1 0 0 1 1 1v12a1 1 0 0 1-1 1v-1c0-1-1-4-6-4s-6 3-6 4v1a1 1 0 0 1-1-1V2a1 1 0 0 1 1-1h12z"/>
              </svg>
              {{ userData.username }}
            </div>

            <form method="post" action="/accounts/logout/" class="d-flex my-2 my-md-0">
              <input type="hidden" name="csrfmiddlewaretoken" :value="getCsrfToken()">
              <input type="hidden" name="next" :value="getCurrentUrl()">
              <button type="submit" class="btn btn-secondary">Log Out</button>
            </form>
          </template>
          <template v-else>
            <Modal modalTitle="Log In"
                   modalButtonText="Log In"
                   acceptButtonText="Log in via Reddit"
                   :acceptButtonPost="userData.authenticationUrl">
              To fill in surveys, you must be logged in with a Reddit account.
            </Modal>
          </template>
        </div>
      </div>
    </div>
  </nav>
</template>

<script lang="ts">
import Modal from '@/components/Modal.vue';
import { Options, Vue } from 'vue-class-component';
import Cookie from 'js-cookie';
import type { UserData } from '@/util/data';
import UserService from '@/util/user-service';

@Options({
  components: {
    Modal,
  },
})
export default class TheNavbar extends Vue {
  userData: UserData | null = null;

  async created(): Promise<void> {
    this.userData = await UserService.getUserData();
  }
  
  getCurrentUrl(): string {
    return window.location.href;
  }

  getCsrfToken(): string | undefined {
    return Cookie.get('csrftoken');
  }
}
</script>
