import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import FileUploadView from '../views/FileUploadView.vue'
import LoginView from '../views/LoginView.vue'
import HistoryView from '../views/HistoryView.vue'
import ResultView from '@/views/ResultView.vue'
import DirectInputView from '@/views/DirectInputView.vue'
import EmotionTrendOverTime from '@/views/EmotionTrendOverTime.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView
    },
    {
      path: '/about',
      name: 'about',
      // route level code-splitting
      // this generates a separate chunk (About.[hash].js) for this route
      // which is lazy-loaded when the route is visited.
      component: () => import('../views/AboutView.vue')
    },
    {
      path: '/fileUpload',
      name: 'fileUpload',
      component: FileUploadView
    },
    {
      path: '/login',
      name: 'login',
      component: LoginView
    },
    {
      path: '/history',
      name: 'history',
      component: HistoryView
    },
    {
      path: '/history/:resultId',
      name: 'result',
      component: ResultView
    },
    {
      path: '/directInput',
      name: 'directInput',
      component: DirectInputView
    },
    {
      path: '/emotionTrendOverTime',
      name: 'emotionTrendOverTime',
      component: EmotionTrendOverTime
    }

    
  ]
})

export default router
