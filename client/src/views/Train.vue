<!-- 主界面 -->
<template>
    <div class="container">
        <el-form label-position="top" label-width="100px" class="demo-ruleForm" :model="ruleForm" :rules="rules" status-icon
            ref="ruleForm">
            <el-form-item label="训练集" prop="value1" style="margin-top: 4%;">
                <el-select v-model="ruleForm.value1" placeholder="请选择训练集">
                    <el-option v-for="item in ds_name" :key="item" :label="item" :value="item">
                    </el-option>
                </el-select>
            </el-form-item>
            <el-form-item label="模型" prop="value2">
                <el-select v-model="ruleForm.value2" placeholder="请选择模型">
                    <el-option v-for="item in model" :key="item" :label="item" :value="item">
                    </el-option>
                </el-select>
            </el-form-item>
            <div style="text-align: center;margin-top: 30%;margin-bottom: 3%;">
                <el-button slot="trigger" size="small" type="primary">训练</el-button>
            </div>
        </el-form>
    </div>
</template>
<script>
import axios from 'axios'
import Cookies from 'js-cookie'
export default {
    data() {
        return {
            rules: {
                value1: [
                    { required: true, trigger: 'change' }
                ],
                value2: [
                    { required: true, trigger: 'change' }
                ],
            },
            ds_name: [],
            model: [
                'yolo_v5'
            ],
            ruleForm: {
                value1: '',
                value2: '',
            }
        }
    },
    created() {
        // 从后台获取数据集列表
        axios.get('http://127.0.0.1:5000/model/detect', {
            params: {
                step: '1'
            },
            headers: {
                'Authorization': 'Bearer ' + Cookies.get('token'),
                'Content-Type': "application/json"
            }
        })
            .then((response) => {
                console.log(response)
                this.ds_name = response.data
            })
            .catch((error) => {
                console.error(error);
            });
    },
    methods: {

    }
}
</script>

<style lang="less" scoped>
.container {
    position: absolute;
    box-shadow: 4px 4px 10px rgba(0, 0, 0, 0.2);
    background-color: #fff;
    top: 50%;
    left: 50%;
    width: 20rem;
    height: 25rem;

    .el-select {
        position: relative;
        margin: 0%;
        margin-left: 10%;
    }
}
</style>