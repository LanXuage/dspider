<template>
    <el-form @keyup.enter.native="submitForm(formDataRef)" ref="formDataRef" :model="formData" status-icon
        :rules="rules" label-width="120px" class="demo-formData">
        <el-form-item :label="$t('username')" prop="username">
            <el-input v-model="formData.username" autocomplete="off" :placeholder="$t('pleaseInputUname')">
                <template #prefix>
                    <el-icon>
                        <User />
                    </el-icon>
                </template>
            </el-input>
        </el-form-item>
        <el-form-item :label="$t('password')" prop="password">
            <el-input v-model="formData.password" type="password" autocomplete="off"
                :placeholder="$t('pleaseInputPass')" show-password>
                <template #prefix>
                    <el-icon>
                        <Lock />
                    </el-icon>
                </template>
            </el-input>
        </el-form-item>
        <el-form-item>
            <el-button type="primary" @click="submitForm(formDataRef)" :loading-icon="Eleme"
                :loading="formData.logingin" :disabled="formData.logingin">
                {{ formData.logingin ? $t('logingin') : $t('login') }}
            </el-button>
        </el-form-item>
    </el-form>
</template>

<script lang="ts" setup>
import { reactive, ref } from 'vue'
import type { FormInstance } from 'element-plus'
import { Eleme, User, Lock } from '@element-plus/icons-vue'

import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'

import { useAuthUserStore } from '@/stores'

const formDataRef = ref<FormInstance>()

const router = useRouter()

const { t } = useI18n()

const validatePass = (rule: any, value: any, callback: any) => {
    if (value === '') {
        callback(new Error(t('pleaseInputPass')))
    } else {
        if (formData.username !== '') {
            if (!formDataRef.value) return
            formDataRef.value.validateField('password', () => null)
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

const formData = reactive({
    username: '',
    password: '',
    logingin: false
})


const rules = reactive({
    username: [{ validator: validateUname, trigger: 'blur' }],
    password: [{ validator: validatePass, trigger: 'blur' }],
})

const submitForm = (formEl: FormInstance | undefined) => {
    if (!formEl) return
    formEl.validate(async (valid) => {
        if (valid) {
            formData.logingin = true
            const authUser = useAuthUserStore()
            if (await authUser.login(formData)) {
                router.push('/')
            } else {
                formData.logingin = false
            }
        } else {
            return false
        }
    })
}
</script>
