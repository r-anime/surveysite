<template>
  <div class="home">
    <img alt="Vue logo" src="../assets/logo.png">
    <p>
      abcdef:<br>
      {{ data }}
    </p>
  </div>
</template>

<script lang="ts">
import { Options, Vue } from 'vue-class-component';
import HelloWorld from '@/components/HelloWorld.vue';
import Ajax from '@/util/ajax';


@Options({
  components: {
    HelloWorld,
  },
  data() {
    return {
      data: {}
    }
  },
  methods: {
  },
  async mounted() {
    this.data = await Ajax.get<any>('api/index/');
  }
})
export default class Index extends Vue {}
</script>
