<template>
    <el-form ref="userDataRef" :model="userData" status-icon :rules="rules" label-width="120px" class="demo-userData">
        <el-form-item label="USERNAME" prop="username">
            <el-input v-model="userData.username" autocomplete="off" placeholder="Please input username" />
        </el-form-item>
        <el-form-item label="PASSWORD" prop="password">
            <el-input v-model="userData.password" type="password" autocomplete="off" placeholder="Please input password"
                show-password />
        </el-form-item>
        <el-form-item>
            <el-button type="primary" @click="submitForm(userDataRef)" :loading-icon="Eleme" :loading="logining"
                :disabled="logining">Login
            </el-button>
        </el-form-item>
    </el-form>
</template>

<script lang="ts" setup>
import { reactive, ref } from 'vue'
import type { FormInstance } from 'element-plus'
import { Eleme } from '@element-plus/icons-vue'

import { useRouter } from 'vue-router'

import { User } from '@/api/user'

const userDataRef = ref<FormInstance>()

const router = useRouter()

const validatePass = (rule: any, value: any, callback: any) => {
    if (value === '') {
        callback(new Error('Please input the username'))
    } else {
        if (userData.username !== '') {
            if (!userDataRef.value) return
            userDataRef.value.validateField('password', () => null)
        }
        callback()
    }
}

const validateUname = (rule: any, value: any, callback: any) => {
    if (value === '') {
        callback(new Error('Please input the password again'))
    } else {
        callback()
    }
}

const userData = reactive({
    username: '',
    password: '',
})

const logining = ref(false)

const rules = reactive({
    username: [{ validator: validateUname, trigger: 'blur' }],
    password: [{ validator: validatePass, trigger: 'blur' }],
})

const submitForm = (formEl: FormInstance | undefined) => {
    logining.value = true
    if (!formEl) return
    formEl.validate(async (valid) => {
        if (valid) {
            let user = new User(userData)
            if (await user.login()) {
                router.push('/')
            } else {
                logining.value = false
            }
        } else {
            return false
        }
    })
}
</script>
