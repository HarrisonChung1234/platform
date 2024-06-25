<template>
    <div>
        <h3 style="display:inline-block">选择需要使用的功能： </h3>
        <el-button slot="trigger" size="small" type="primary" @click="toTrain">训练模型</el-button>
        <el-button slot="trigger" size="small" type="primary" @click="toDetect">检测图片</el-button>
        <div>
            <router-view></router-view>
        </div>
    </div>
</template>
<script>
export default {
    data() {
        return {}
    },
    methods: {
        toDetect() {
            this.$router.push('/model/detect')
            //面包屑
            this.$store.commit('pushCrumb', { label: '检测图片', path: '/model/detect', name: 'detect' })
        },
        toTrain() {
            this.$router.push('/model/train')
            //面包屑
            this.$store.commit('pushCrumb', { label: '训练模型', path: '/model/train', name: 'train' })
        }
    },
}
</script>