<template>
    <div>
        <div class="container">
            <el-form label-position="top" label-width="100px" class="demo-ruleForm" :model="ruleForm" :rules="rules"
                status-icon ref="ruleForm">
                <el-form-item label="训练集" prop="value1" style="margin-top: 4%;">
                    <el-select v-model="ruleForm.value1" placeholder="请选择训练集">
                        <el-option v-for="item in model_name" :key="item" :label="item" :value="item">
                        </el-option>
                    </el-select>
                </el-form-item>
                <el-form-item label="模型" prop="value2">
                    <el-select v-model="ruleForm.value2" placeholder="请选择模型">
                        <el-option v-for="item in model_type" :key="item" :label="item" :value="item">
                        </el-option>
                    </el-select>
                </el-form-item>
                <el-form-item label="测试集" prop="value3">
                    <el-select v-model="ruleForm.value3" placeholder="请选择要检测的数据集">
                        <el-option v-for="item in p_set" :key="item" :label="item" :value="item">
                        </el-option>
                    </el-select>
                </el-form-item>
                <el-form-item @change="getPicList" label="测试集中的照片" prop="value4">
                    <el-select v-model="ruleForm.value4" :disabled="p_name.length === 0 ? true : false"
                        placeholder="请先选择要检测的数据集">
                        <el-option v-for="item in p_name" :key="item" :label="item" :value="item">
                        </el-option>
                    </el-select>
                </el-form-item>
                <div style="text-align: center;margin-top: 10%;margin-bottom: 3%;">
                    <el-button slot="trigger" size="small" type="primary" @click="submitDetect">检测</el-button>
                </div>
            </el-form>
        </div>
        <div class="rcontainer">
            <div class="imgPart" v-if="img_stream">
                <img :src="'data:;base64,' + img_stream" style="width: 480px;" @click="startDownload">
                <h3 style="text-align: center;">点击图片即可下载标记后的图片</h3>
            </div>
            <div class="textPart" v-else>
                <h1 style="font-size: 40px;">检测后的图片会显示在这</h1>
            </div>
        </div>
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
                value3: [
                    { required: true, trigger: 'change' }
                ],
                value4: [
                    { required: true, trigger: 'change' }
                ]
            },
            ruleForm: {
                value1: '',
                value2: '',
                value3: '',
                value4: '',
            },
            model_name: [],
            model_type: [
                'yolo_v5'
            ],
            p_set: [],
            p_name: ['PCB1.jpg','PCB2.jpg','PCB3.jpg','PCB4.jpg','PCB5.jpg','PCB6.jpg','PCB7.jpg',],
            img_stream: '',
            img_url: ''
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
                this.model_name = response.data
                this.p_set = response.data
            })
            .catch((error) => {
                console.error(error);
            });
    },
    methods: {
        getPicList(value) {
            // 获取图片罢
            axios.get('http://127.0.0.1:5000/model/detect', {
                params: {
                    step: '2',
                    ds_name: value
                },
                headers: {
                    'Authorization': 'Bearer ' + Cookies.get('token'),
                    'Content-Type': "application/json"
                }
            }).then((response) => {
                this.p_name = response.data.image_names
            }).catch((error) => {
                console.log(error.data)
            });
        },
        submitDetect() {
            axios.post('http://127.0.0.1:5000/model/detect', {
                model_name: this.ruleForm.value1,
                model_type: this.ruleForm.value2,
                p_set: this.ruleForm.value3,
                p_name: this.ruleForm.value4
            }, {
                headers: {
                    'Authorization': 'Bearer ' + Cookies.get('token'),
                    'Content-Type': 'application/json'
                }
            }).then((response) => {
                this.img_stream = response.data
            }).catch((error) => {
                console.error(error);
            });
        },
        startDownload() {
            // 创建一个链接元素
            var a = document.createElement('a')
            a.href = 'data:;base64,' + this.img_stream// 图片的URL
            a.download = this.ruleForm.value4
            document.body.appendChild(a)
            a.click()
            document.body.removeChild(a)
        }
    }
}
</script>

<style lang="less" scoped>
.container {
    position: absolute;
    box-shadow: 4px 4px 10px rgba(0, 0, 0, 0.2);
    top: 58%;
    left: 32%;
    width: 20rem;
    height: 33rem;
    background-color: #fff;

    .el-select {
        position: relative;
        margin: 0%;
        margin-left: 10%;
    }
}

.rcontainer {
    .textPart {
        position: absolute;
        top: 45%;
        left: 55%;
    }

    .imgPart {
        position: absolute;
        top: 27%;
        left: 55%;
    }
}
</style>