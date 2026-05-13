import { createRouter, createWebHashHistory } from 'vue-router'
import { useAuthStore } from 'src/stores/auth'

const routes = [
    {
        path: '/login',
        component: () => import('src/layouts/AuthLayout.vue'),
        meta: { public: true },
        children: [
            {
                path: '',
                name: 'Login',
                component: () => import('src/pages/LoginPage.vue'),
            },
        ],
    },
    {
        path: '/',
        component: () => import('src/layouts/MainLayout.vue'),
        meta: { requiresAuth: true },
        children: [
            {
                path: '',
                redirect: '/dashboard',
            },
            {
                path: 'dashboard',
                name: 'Dashboard',
                component: () => import('src/pages/DashboardPage.vue'),
            },
            {
                path: 'incidents',
                name: 'Incidents',
                component: () => import('src/pages/IncidentsPage.vue'),
            },
            {
                path: 'incidents/create',
                name: 'CreateIncident',
                component: () => import('src/pages/CreateIncidentPage.vue'),
                meta: { roles: ['admin', 'manager'] },
            },
            {
                path: 'incidents/:id',
                name: 'IncidentDetail',
                component: () => import('src/pages/IncidentDetailPage.vue'),
            },
            {
                path: 'users',
                name: 'Users',
                component: () => import('src/pages/UsersPage.vue'),
                meta: { roles: ['admin'] },
            },
        ],
    },
    {
        path: '/:catchAll(.*)*',
        redirect: '/dashboard',
    },
]

const router = createRouter({
    history: createWebHashHistory(),
    routes,
})

router.beforeEach((to, from, next) => {
    const authStore = useAuthStore()

    if (to.meta.public) {
        if (authStore.isAuthenticated && to.name === 'Login') {
            return next('/dashboard')
        }
        return next()
    }

    if (!authStore.isAuthenticated) {
        return next('/login')
    }

    // Role guard
    if (to.meta.roles && !to.meta.roles.includes(authStore.user?.role)) {
        return next('/dashboard')
    }

    next()
})

export default router
