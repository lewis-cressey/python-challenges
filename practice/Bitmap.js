export class Bitmap {
    constructor(hex) {
        this.data = []

        hex = hex ?? ""
        for (let i = 0; i < hex.length; i += 2) {
            const byte = hex.substring(i, 2)
            const value = parseInt(byte, 16)
            this.data.push(value)
        }
    }

    testBit(n) {
        const addr = n >> 3
        const bitmask = 1 << (n & 7)
        if (addr >= this.data.length) return false
        return (this.data[addr] & bitmask) != 0
    }

    setBit(n) {
        const addr = n >> 3
        const bitmask = 1 << (n & 7)
        while (addr >= this.data.length) this.data.push(0)
        this.data[addr] |= bitmask
    }

    toString() {
        const data = this.data.map(x => x.toString(16).padStart(2, '0'))
        return data.join("")
    }
}
