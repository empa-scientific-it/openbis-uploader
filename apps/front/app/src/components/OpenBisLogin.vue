<template>
  <div class="login" @submit.prevent="onSubmit">
        <form novalidate>
            <h3>Sign in to OpenBIS instance</h3>
            <div class="row">
                <label for="user">Username</label>
                <input type="text" v-model="user" id="user" />
            </div>
            <div class="row">
                <label for="password">Password</label>
                <input type="password" v-model="password"  id="password"/>
            </div>
            <div class="row">
              <button type="submit" class="btn btn-dark btn-lg btn-block" @click="onSubmit">Sign In</button>
            </div>
        </form>
  </div>
</template>

<script setup lang="ts">
  import { useUser } from '@/stores/login';
  import { useRouter, useRoute } from 'vue-router'
  import { ref } from 'vue'
  import type { Ref } from 'vue'
  
  const user: Ref<string> = ref("");
  const password: Ref<string> = ref("");


  const store = useUser();
  const router = useRouter();
  
  async function onSubmit(ev: Event){
    const success = await store.login(user.value, password.value);
    if(success){
      router.push({'name':"eln"});
    }
  }
</script>

<style>

div.form
{
    display: block;
    text-align: center;
}

label {
    width:180px;
    clear:left;
    text-align:right;
    padding-right:10px;
}

input, label {
    float:left;
}

form
{
    display: inline-block;
    margin-left: auto;
    margin-right: auto;
    text-align: left;
}



</style>