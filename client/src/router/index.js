import Vue from 'vue'
import VueRouter from 'vue-router'
import store from '@/store'
import { Notification } from 'element-ui'
Vue.use(VueRouter)
/* 
    1、创建路由组件
    首先在src源代码文件夹中创建一个views文件夹
    views文件夹中放需要的路由组件，一个界面就是一个路由组件
    最后再在路由配置index.js中import进来
*/
import User from '../views/User.vue'
import Login from '../views/Login.vue'
import Main from '../views/Main.vue'
import Instruction from '../views/Instruction.vue'
import MarkPic from '../views/MarkPic.vue'
import Model from '../views/Model.vue'
import Detect from '../views/Detect.vue'
import Train from '../views/Train.vue'
import NotFound from '../views/NotFound.vue'
import todevelop from '../views/todevelop.vue'
import contactus from '../views/contactus.vue'

/*
    2、将组件和路由做一个映射
    采用数组方式，数组中放键值对
    代表component的对应path
*/
const routes = [
    // 主路由
    {
        path: '/',
        component: Main,
        redirect: '/user',  //重定向
        children: [
            // 子路由
            { path: 'login', name: 'Login', component: Login },//登录页
            { path: 'user', name: 'User', component: User },  //用户数据管理
            { path: 'instruction', name: 'Instruction', component: Instruction },    //使用说明
            { path: 'markpic', name: 'Markpic', component: MarkPic }, //标注图片
            { path: 'xiba', name: 'xiba', component: todevelop },
            { path: 'loma', name: 'loma', component: todevelop },
            { path: 'kesagi', name: 'kesagi', component: contactus },

            {
                path: 'model',
                component: Model,
                redirect: '/model/train',
                children: [
                    { path: 'detect', component: Detect, name: 'Detect' },
                    { path: 'train', component: Train, name: 'Train' }
                ]
            } //检测或者训练
        ]
    },
    { path: '*', component: NotFound } //404
]
/*
    3、创建router实例，然后传router配置
*/
const router = new VueRouter({
    routes,
    mode: "history"
})
/*
这样做的目的是为了避免在使用 push 方法进行导航时，如果出现错误（例如路由跳转失败）导致的控制台报错。
通过添加 .catch(err => err)，错误将被捕捉并作为结果返回，从而防止错误的抛出。
*/
const originalPush = VueRouter.prototype.push
VueRouter.prototype.push = function push(location) {
    return originalPush.call(this, location).catch(err => err)
}
//添加全局导航守卫
router.beforeEach((to, from, next) => {
    //判断token存不存在即登没登陆
    const token = store.state.user.userInfo.cookie
    if (!token && (to.name === 'User' || to.name === 'Loadpic' || to.name === 'Markpic' || to.name==='Detect' || to.name==='Train')) {
        //未登录需要跳转至登录页
        next({ name: 'Login' })
        Notification({
            title: '消息',
            message: '您还未登录',
            position: 'bottom-right',
            type: 'warning'
        })
    }
    if (token && to.name === 'Login') {
        next({ name: 'User' })
    }
    next()
})
//  4、向外暴露，在main.js中import挂载到根节点上
export default router