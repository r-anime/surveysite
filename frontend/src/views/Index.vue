<template>
  <div class="home">
    <img alt="Vue logo" src="../assets/logo.png">
    <p>
      abcdef:<br>
      {{ api }}
    </p>
  </div>
</template>

<script lang="ts">
import { Options, Vue } from 'vue-class-component';
import HelloWorld from '@/components/HelloWorld.vue'; // @ is an alias to /src
import axios from 'axios';


@Options({
  components: {
    HelloWorld,
  },
  data() {
    return {
      api: ""
    }
  },
  methods: {
    async getData() {
      let result;
      console.log('getData() called');
      try {
        console.log('Calling api');
        const response = await axios.get('api/index/');
        result = response.data;
        console.log('Got api response: ');
        console.log(result);
      }
      catch (e) {
        if (e.response) {
          result = 'Server error: ' + e.toString();
        }
        else if (e.request) {
          result = 'Network error: ' + e.toString();
        }
        else {
          result = 'Client error: ' + e.toString();
        }
      }

      this.api = result;
    }
  },
  mounted() {
    this.getData();
  }
})
export default class Index extends Vue {}
</script>
