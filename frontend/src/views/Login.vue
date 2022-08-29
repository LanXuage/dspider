<template>
    <div class="container">
        <div class="login"></div>
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
        background-color: cyan;
        display: flex;
        justify-content: right;
        align-items: center;
        .login {
            margin-right: 15vw;
            width: 400px;
            height: 350px;
            background-color: white;
            border-radius: 6px;
        }
    }
</style>