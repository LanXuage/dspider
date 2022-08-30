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
}

export { Msg }
