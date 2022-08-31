<template>
    <el-form @keyup.enter.native="submitForm(userDataRef)" ref="userDataRef" :model="userData" status-icon :rules="rules" label-width="120px" class="demo-userData">
        <el-form-item :label="$t('username')" prop="username">
            <el-input v-model="userData.username" autocomplete="off" :placeholder="$t('pleaseInputUname')" />
        </el-form-item>
        <el-form-item :label="$t('password')" prop="password">
            <el-input v-model="userData.password" type="password" autocomplete="off" :placeholder="$t('pleaseInputPass')"
                show-password />
        </el-form-item>
        <el-form-item>
            <el-button type="primary" @click="submitForm(userDataRef)" :loading-icon="Eleme" :loading="logining"
                :disabled="logining">{{$t('login')}}
            </el-button>
        </el-form-item>
    </el-form>
</template>

<script lang="ts" setup>
import { reactive, ref } from 'vue'
import type { FormInstance } from 'element-plus'
import { Eleme } from '@element-plus/icons-vue'

import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'

import { User } from '@/api/user'

const userDataRef = ref<FormInstance>()

const router = useRouter()

const { t } = useI18n()

const validatePass = (rule: any, value: any, callback: any) => {
    if (value === '') {
        callback(new Error(t('pleaseInputPass')))
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
        callback(new Error(t('pleaseInputUname')))
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
    if (!formEl) return
    formEl.validate(async (valid) => {
        if (valid) {
            logining.value = true
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
