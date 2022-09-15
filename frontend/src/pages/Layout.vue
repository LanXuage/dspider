<template>
    <div class="common-layout">
        <el-container>
            <el-header class="header">
                <el-menu active-text-color="#fff" background-color="#545c64" text-color="#fff" class="el-menu"
                    mode="horizontal" :ellipsis="false" @select="handleSelect">
                    <el-menu-item index="" @click="isCollapse=!isCollapse">
                        <el-icon>
                            <Expand v-if="isCollapse" />
                            <Fold v-else />
                        </el-icon>
                    </el-menu-item>
                    <el-menu-item index="1">DSPIDER</el-menu-item>
                    <div class="flex-grow" />
                    <el-sub-menu index="2"><template #title>Lang</template>
                        <el-menu-item index="2-1">中文</el-menu-item>
                        <el-menu-item index="2-2">English</el-menu-item>
                    </el-sub-menu>
                </el-menu>
            </el-header>
            <el-container>
                <el-aside width="collapse">
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
                </el-container>
            </el-container>
        </el-container>
    </div>
</template>

<script lang="ts" setup>
import { ref } from 'vue'
import {
    Fold,
    Expand,
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
    min-height: 56px;
    height: 6vh;
    padding: 0;

    .flex-grow {
        flex-grow: 1;
    }

    .el-menu {
        min-height: 56px;
        height: 6vh;
    }

    .el-menu-item {
        user-select: none;
    }

    .el-menu--horizontal {
        border-bottom: 0;
    }

    .el-icon {
        margin: 0;
    }
}

.el-aside {
    margin: 0;

    .el-menu {
        min-height: 94vh;
    }

    .el-menu--vertical:not(.el-menu--collapse) {
        width: 200px;
    }

}

.el-main {
    height: 94vh;
}

.el-menu--horizontal>.el-menu-item.is-active {
    border-bottom: 0;
}

.el-menu--horizontal>.el-menu-item {
    border-bottom: 0;
}
</style>