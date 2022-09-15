<template>
    <el-form :model="form" label-width="200px">
        <el-form-item label="URL">
            <el-input v-model="form.url" />
        </el-form-item>
        <el-form-item label="Method">
            <el-select v-model="form.method" placeholder="Please select request method">
                <el-option label="GET" value="GET" />
                <el-option label="POST" value="POST" />
            </el-select>
        </el-form-item>
        <el-form-item label="Headers">
            <el-input v-model="form.headers" type="textarea" />
        </el-form-item>
        <el-form-item label="Payload">
            <el-input v-model="form.payload" type="textarea" />
        </el-form-item>
        <el-form-item label="Timeout">
            <el-input-number v-model="form.timeout" :min="15" :max="100" />
        </el-form-item>
        <el-form-item label="Use Robots">
            <el-switch v-model="form.useRobots" :active-icon="Check" :inactive-icon="Close" />
        </el-form-item>
        <el-form-item label="Use Tor">
            <el-switch v-model="form.useTor" :active-icon="Check" :inactive-icon="Close" :disabled="true" />
        </el-form-item>
        <el-form-item label="Use Proxy">
            <el-switch v-model="form.useProxy" :active-icon="Check" :inactive-icon="Close" :disabled="true" />
        </el-form-item>
        <el-form-item label="Generator ID">
            <el-input v-model="form.generatorId" />
        </el-form-item>
        <el-form-item label="Generator Configuration">
            <el-input v-model="form.generatorCfg" type="textarea" />
        </el-form-item>
        <el-form-item label="Matcher ID">
            <el-input v-model="form.matcherId" />
        </el-form-item>
        <el-form-item label="Matcher Configuration">
            <el-input v-model="form.matcherCfg" type="textarea" />
        </el-form-item>
        <el-form-item label="Exporter ID">
            <el-input v-model="form.exporterId" />
        </el-form-item>
        <el-form-item label="Exporter Configuration">
            <el-input v-model="form.exporterCfg" type="textarea" />
        </el-form-item>
        <el-form-item label="Is Periodic">
            <el-switch v-model="form.isPeriodic" :active-icon="Check" :inactive-icon="Close" />
        </el-form-item>
        <el-form-item label="Crontab Expression">
            <el-input v-model="form.cronExpn" />
        </el-form-item>
        <el-form-item label="Request Interval">
            <el-input-number v-model="form.reqInterval" :min="15" :max="100" />
        </el-form-item>
        <el-form-item label="Start Time">
            <el-date-picker v-model="form.startTime" type="datetime" placeholder="Select date and time" />
        </el-form-item>
        <el-form-item>
            <el-button type="primary" @click="onSubmit">Create Task</el-button>
        </el-form-item>
    </el-form>
</template>

<script lang="ts" setup>
import { reactive, ref } from 'vue'
import { Check, Close } from '@element-plus/icons-vue'

const form = reactive({
    url: '',
    method: 'GET',
    headers: '',
    payload: '',
    timeout: 15,
    useRobots: false,
    useTor: false,
    useProxy: false,
    generatorId: '',
    generatorCfg: '',
    matcherId: '',
    matcherCfg: '',
    exporterId: '',
    exporterCfg: '',
    isPeriodic: false,
    cronExpn: '',
    reqInterval: 15,
    startTime: ''
})

const onSubmit = () => {
    console.log(form)
    console.log('submit!')
}
</script>