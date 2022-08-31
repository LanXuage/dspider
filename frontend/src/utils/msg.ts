import { ElMessage } from 'element-plus'

class Msg {
    static success(message: string, showClose = true, duration = 1000): void {
        ElMessage({
            showClose: showClose,
            message: message,
            duration: duration,
            type: 'success',
        })
    }

    static warning(message: string, showClose = true, duration = 1000): void {
        ElMessage({
            showClose: showClose,
            message: message,
            duration: duration,
            type: 'warning',
        })
    }

    static error(message: string, showClose = true, duration = 1000): void {
        ElMessage({
            showClose: showClose,
            message: message,
            duration: duration,
            type: 'error',
        })
    }
}

export { Msg }
