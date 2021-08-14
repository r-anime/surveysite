<template>
  <nav class="navbar navbar-expand-md bg-light sticky-top navbar-light">
    <div class="container-fluid">
      <router-link to="/" class="navbar-brand">/r/anime Surveys</router-link>

      <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav"
        aria-controls="navbarNav" aria-expanded="false" aria-label="Toggle navigation"
      >
        <span class="navbar-toggler-icon"></span>
      </button>

      <div class="collapse navbar-collapse" id="navbarNav">
        <div class="navbar-nav ms-auto">
          <template v-if="userData.authenticated">
            <div class="navbar-text me-3 my-2 my-md-0">
              Logged in as
              <img v-if="userData.profilePicture" class="mx-1 my-n3 align-middle rounded border" style="width:auto;height:35px;" :src="userData.profilePicture">
              <svg v-else xmlns="http://www.w3.org/2000/svg" width="25" height="25" fill="currentColor" class="bi mx-1 my-n2" viewBox="0 0 16 16">
                <path d="M11 6a3 3 0 1 1-6 0 3 3 0 0 1 6 0z"/>
                <path d="M2 0a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V2a2 2 0 0 0-2-2H2zm12 1a1 1 0 0 1 1 1v12a1 1 0 0 1-1 1v-1c0-1-1-4-6-4s-6 3-6 4v1a1 1 0 0 1-1-1V2a1 1 0 0 1 1-1h12z"/>
              </svg>
              {{ userData.username }}
            </div>

            <form method="post" action="/accounts/logout/" class="d-flex my-2 my-md-0">
              <input type="hidden" name="csrfmiddlewaretoken" :value="csrfToken">
              <input type="hidden" name="next" :value="currentUrl">
              <button type="submit" class="btn btn-secondary">Log Out</button>
            </form>
          </template>
          <template v-else>
            <ModalButton id="loginModal" variant="primary">Log In</ModalButton>
          </template>
        </div>
      </div>
    </div>
  </nav>

  <Modal id="loginModal"
         title="Log In"
         acceptButtonText="Log in via Reddit"
         acceptButtonUrl="/accounts/login/">
    To fill in surveys, you must be logged in with a Reddit account.
  </Modal>
</template>

<script lang="ts">
import Modal from '@/components/Modal.vue';
import ModalButton from '@/components/ModalButton.vue';
import { Options, Vue } from 'vue-class-component';
import Cookie from 'js-cookie';
import Ajax from '@/util/ajax';

class UserData {
  authenticated = false;
  username?: string;
  profilePicture?: string;
}

@Options({
  components: {
    Modal,
    ModalButton,
  },
  data() {
    return {
      userData: {} as UserData,
      currentUrl: window.location.href,
      csrfToken: Cookie.get('csrftoken') ?? '',
    }
  },
  methods: {
    
  },
  async mounted() {
    this.userData = await Ajax.get<UserData>('api/user/') ?? new UserData();
  }
})
export default class TheNavbar extends Vue {}
</script>
