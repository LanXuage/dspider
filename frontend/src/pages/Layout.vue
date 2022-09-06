<template>
    <div class="common-layout">
        <el-container>
            <el-header class="header">
                <el-menu active-text-color="#fff" background-color="#545c64" text-color="#fff" class="el-menu"
                    mode="horizontal" :ellipsis="false" @select="handleSelect">
                    <el-radio-group v-model="isCollapse">
                        <el-radio-button :label="false">expand</el-radio-button>
                        <el-radio-button :label="true">collapse</el-radio-button>
                    </el-radio-group>
                    <el-menu-item index="1">LOGO</el-menu-item>
                    <div class="flex-grow" />
                    <el-sub-menu index="2"><template #title>Lang</template>
                        <el-menu-item index="2-1">中文</el-menu-item>
                        <el-menu-item index="2-2">English</el-menu-item>
                        <el-menu-item index="2-3">Others</el-menu-item>
                    </el-sub-menu>
                </el-menu>
            </el-header>
            <el-container>
                <el-aside class="aside">
                    <el-menu active-text-color="#ffd04b" background-color="#545c64" text-color="#fff"
                        :default-active="$route.path.substring(1)" class="el-menu" :collapse="isCollapse"
                        @open="handleOpen" @close="handleClose" router>
                        <el-menu-item index="dashboard">
                            <el-icon>
                                <Monitor />
                            </el-icon>
                            <template #title>Dashboard</template>
                        </el-menu-item>
                        <el-menu-item index="task">
                            <el-icon>
                                <Odometer />
                            </el-icon>
                            <template #title>Task Center</template>
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
    Fold,
    Monitor,
    Odometer,
    InfoFilled
} from '@element-plus/icons-vue'

const isCollapse = ref(false)
const handleOpen = (key: string, keyPath: string[]) => {
    console.log(key, keyPath)
}
const handleClose = (key: string, keyPath: string[]) => {
    console.log(key, keyPath)
}

const handleSelect = (key: string) => {
    console.log(key)
}
</script>

<style lang="scss">
.header {
    height: 6vh;
    padding: 0;

    .flex-grow {
        flex-grow: 1;
    }

    .el-menu {
        height: 6vh;
    }

    .el-menu--horizontal {
        border-bottom: 0;
    }
}

.aside {
    margin: 0;

    .el-menu {
        min-height: 94vh;
    }

    width: auto;
}
</style>