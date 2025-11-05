import { createRouter, createWebHistory } from 'vue-router';
import UploadPage from '../views/UploadPage.vue';
import StatusPage from '../views/StatusPage.vue';

const routes = [
  {
    path: '/',
    name: 'Upload',
    component: UploadPage,
    meta: {
      title: 'EC2 Control Portal - Upload',
    },
  },
  {
    path: '/status',
    name: 'Status',
    component: StatusPage,
    meta: {
      title: 'EC2 Control Portal - Status',
    },
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

router.beforeEach((to, from, next) => {
  document.title = to.meta.title || 'EC2 Control Portal';
  next();
});

export default router;
