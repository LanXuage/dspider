<template>
    <div class="common-layout">
        <el-container>
            <el-header class="header">Header</el-header>
            <el-container>
                <el-aside width="240px">
                    <el-menu active-text-color="#ffd04b" background-color="#545c64" text-color="#fff"
                        :default-active="$route.path.substring(1)" class="el-menu" :collapse="isCollapse" @open="handleOpen"
                        @close="handleClose" router>
                        <el-menu-item index="dashboard">
                            <el-icon>
                                <Monitor />
                            </el-icon>
                            <template #title>Dashboard</template>
                        </el-menu-item>
                        <el-menu-item index="about">
                            <el-icon>
                                <InfoFilled />
                            </el-icon>
                            <template #title>About</template>
                        </el-menu-item>
                    </el-menu>
                </el-aside>
                <el-container>
                    <el-main>
                        <router-view></router-view>
                    </el-main>
                    <el-footer>Footer</el-footer>
                </el-container>
            </el-container>
        </el-container>
    </div>
</template>

<script lang="ts" setup>
import { ref } from 'vue'
import {
    Monitor,
    InfoFilled
} from '@element-plus/icons-vue'

const isCollapse = ref(false)
const handleOpen = (key: string, keyPath: string[]) => {
    console.log(key, keyPath)
}
const handleClose = (key: string, keyPath: string[]) => {
    console.log(key, keyPath)
}
</script>

<style>
.header {
    height: 10vh;
}

.el-menu:not(.el-menu--collapse) {
    width: 240px;
    min-height: 100%;
}

.el-menu:not(.el-menu--expand) {
    min-height: 90vh;
}
</style>