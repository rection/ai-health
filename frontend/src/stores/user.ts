import { defineStore } from 'pinia'
import { ref } from 'vue'
import request from '../api/request'

export interface UserInfo {
  id: number
  username: string
  email: string | null
  avatar: string | null
  gender: string | null
  birthday: string | null
  height_cm: number | null
  weight_kg: number | null
}

export const useUserStore = defineStore('user', () => {
  const user = ref<UserInfo | null>(null)
  const token = ref(localStorage.getItem('token') || '')

  async function fetchUser() {
    if (!token.value) return
    try {
      user.value = await request.get('/users/me')
    } catch {
      logout()
    }
  }

  function setToken(t: string) {
    token.value = t
    localStorage.setItem('token', t)
  }

  function logout() {
    token.value = ''
    user.value = null
    localStorage.removeItem('token')
  }

  return { user, token, fetchUser, setToken, logout }
})
