<script lang="ts" setup>
import LoginForm from '@/components/LoginForm.vue'
</script>
<template>
    <el-row class="container">
        <el-col :lg="16" :md="12"></el-col>
        <el-col :lg="8" :md="12" class="right">
            <LoginForm></LoginForm>
        </el-col>
    </el-row>
</template>
<style lang="scss">
.container {
    min-height: 100vh;
    background-color: aquamarine;

    .right {
        background-color: azure;
        display: flex;
        justify-content: center;
        align-items: center;
        flex-direction: column;
    }
}
</style>