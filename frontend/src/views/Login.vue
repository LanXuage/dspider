<script lang="ts" setup>
import LoginForm from '@/components/LoginForm.vue'
</script>
<template>
    <div class="container">
        <LoginForm class="login"></LoginForm>
    </div>
</template>
<script lang="ts">
export default {
    name: "Login"
}
</script>
<style lang="scss">
.container {
    width: 100vw;
    height: 100vh;
    background-color: gray;
    display: flex;
    justify-content: right;
    align-items: center;

    .login {
        padding: 75px 25px 25px 25px;
        margin-right: 15vw;
        background-color: white;
        border-radius: 6px;
    }
}
</style>