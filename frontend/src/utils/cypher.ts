
import { Base64 } from 'js-base64'

class Cypher {
    static encode(user: any): string {
        return Base64.encode(JSON.stringify(user))
    }

    static decode<T>(userEnc: string | null, c: { new(): T }): T {
        return userEnc ? Object.assign(new c(), JSON.parse(Base64.decode(userEnc))) : new c()
    }
}

export default Cypher
