<template>
  <div class="main-page">
    <!-- 图片预览 -->
    <div class="pics">
      <div class="arrow arrow-left" @click="showMore('down')"></div>
      <div class="pic-container">
        <div class="pic-box" ref="picContainer">
          <div class="pic" v-for="(v, i) in pics" :key="i">
            <div class="info" :style="{ 'background-image': 'url(' + v.url + ')' }"
              @click="activePic(v.url, v.id, i)"></div>
          </div>
        </div>
      </div>
      <div class="arrow arrow-right" @click="showMore('up')"></div>
    </div>

    <el-row :gutter="10" class="tagList" type="flex">
      <draggable
        :distanceRight=rightDistance
        :distanceBottom=bottomDistance
        :isScrollHidden='false' 
        :isCanDraggable='true'
        :zIndex="100">
          <div>
            <el-container class="custom-container">
              <el-row class="button-row" type="flex">
                <el-col>
                  <el-button v-popover:popover1 class="vertical-button" type="primary" icon="el-icon-picture" size="small" @click="handleFileInputClick"></el-button>
                  <el-popover
                    ref="popover1"
                    trigger="hover" 
                    placement="top"
                    width="50"
                  >
                  <p>选择图片</p>
                  </el-popover>
                  <input
                    type="file"
                    ref="fileInput"
                    style="display: none;"
                    @change="handleFileChange"
                  />
                </el-col>
              <el-col>
              <el-button v-popover:popover2 class="vertical-button" type="primary" icon="el-icon-upload" size="small" @click="uploadFile"></el-button>
              <el-popover
                    ref="popover2"
                    trigger="hover" 
                    placement="top"
                    width="50"
                  >
                  <p>上传图片</p>
                  </el-popover>
              </el-col>
              <el-col>
              <el-button v-popover:popover3 class="vertical-button" type="primary" icon="el-icon-delete" size="small" @click="delPic"></el-button>
              <el-popover
                    ref="popover3"
                    trigger="hover" 
                    placement="top"
                    width="50"
                  >
                  <p>删除图片</p>
                  </el-popover>
              </el-col>
            </el-row>
            <el-row class="button-row" type="flex">
              <el-col>
              <el-button v-popover:popover4 class="vertical-button" type="primary" icon="el-icon-full-screen" size="small" @click="addTag"></el-button>
              <el-popover
                    ref="popover4"
                    trigger="hover" 
                    placement="top"
                    width="50"
                  >
                  <p>新增标签类别</p>
                  </el-popover>
              </el-col>
              <el-col>
              <el-button v-popover:popover5 class="vertical-button" type="primary" icon="el-icon-circle-check" size="small" @click="submitForm"></el-button>
              <el-popover
                    ref="popover5"
                    trigger="hover" 
                    placement="top"
                    width="50"
                  >
                  <p>确认标注</p>
                  </el-popover>
              </el-col>
              <el-col>
              <el-button v-popover:popover6 class="vertical-button" type="primary" icon="el-icon-folder-checked" size="small" @click="saveAnno"></el-button>
              <el-popover
                    ref="popover6"
                    trigger="hover" 
                    placement="top"
                    width="50"
                  >
                  <p>保存标注</p>
                  </el-popover>
              </el-col>

            </el-row>
            </el-container>
          </div>
      </draggable>


      <el-col :span="12" class="thirdPart">
        <div class="height-control">
        <ui-marker ref="aiPanel-editor" class="ai-observer" :uniqueKey="currentInfo.uuid" :ratio="currentInfo.rawW / currentInfo.rawH"
          :imgUrl="currentInfo.currentBaseImage" @vmarker:selectOne="selectOne" @vmarker:onUpdated="onUpdated"
          @vmarker:onDrawOne="onDrawOne" @vmarker:onReady="onReady" @vmarker:onImageLoad="onImageLoad"></ui-marker>
        <!-- <canvas ref="canvas" width="currentInfo.currentW" height="currentInfo.currentH"></canvas> -->
        </div>
      </el-col>





      <el-col :span="7" class="firstPart">
        <div class="img-container">
            <img :src="currentInfo.currentBaseImage" class="limited-image">
            <canvas id="anno_canvas" :width="currentInfo.rawW" :height="currentInfo.rawH"></canvas>
            <canvas id="highlighted" :width="currentInfo.rawW" :height="currentInfo.rawH" ></canvas>
        </div>
      </el-col>


      <el-col :span="5" class="secondPart">
        <el-button type="success" class="save-button" @click="saveAll">保存</el-button>
        <div class="title">标签栏</div>
          <el-table :data="tags" max-height="200" border style="width: 100%" :show-header="false">
            <el-table-column label="类别" width="150">
              <template slot-scope="scope">
              <el-tag size="small" @click="setTag(scope.row)">{{ scope.row.tagName }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" >
              <template slot-scope="scope">
                <i class="el-icon-delete" @click="delTag(scope.$index, scope.row.tag)"></i>
              </template>      
            </el-table-column>
          </el-table>
        <!-- <div class="tags" v-for="(v, i) in tags" :key="i">
          <el-tag size="small" @click="setTag(v)">
            {{ v.tagName }}
          </el-tag>
          <i class="el-icon-delete" @click="delTag(i, v.tag)"></i>
        </div> -->
        <div class="title">标注信息</div>
        <div class="annos">
          <el-table :data="currentInfo.data" max-height="300" border style="width: 100%">
            <el-table-column label="id" width="50">
              <template slot-scope="scope">
                <span style="margin-left: 10px">{{ scope.$index + 1}}</span>
              </template>
            </el-table-column>
            <el-table-column label="类别" width="120">
              <!-- <template slot-scope="scope">
                <span style="margin-left: 10px">{{ id2category(scope.row.tag_id)}}</span>
              </template> -->
              <template slot-scope="scope">
                <el-popover trigger="hover" placement="top">
                  <p>左上角x: {{ scope.row.x_ul }}</p>
                  <p>左上角y: {{ scope.row.y_ul }}</p>
                  <p>宽度w: {{ scope.row.wid }}</p>
                  <p>高度h: {{ scope.row.hei }}</p>
                  <div slot="reference" class="name-wrapper">
                    <el-tag size="medium">{{ scope.row.tag_name }}</el-tag>
                  </div>
                </el-popover>
              </template>
            </el-table-column>

            <el-table-column fixed="right" label="操作" width="100">
              <template slot-scope="scope">
                <el-button @click="highlight(scope.row.id)" type="text" size="small">查看</el-button>
                <el-button @click="del_anno(scope.row.id)" type="text" size="small">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </el-col>
      
    </el-row>

    <!-- 添加标签 dialog -->
    <el-dialog width="30%" title="添加标签" :visible.sync="innerVisible" :before-close="beforeClose">
      <el-form ref="innerForm" :model="innerForm" :rules="tep_rules">
        <el-form-item label="标签名称：" prop="tagName">
          <el-input v-model="innerForm.tagName" />
        </el-form-item>
        <!-- <el-form-item label="标签id: " prop="tag">
          <el-input v-model="innerForm.tag" />
        </el-form-item> -->
      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button @click="close">取 消</el-button>
        <el-button type="primary" @click="createForm('innerForm')">
          确 定
        </el-button>
      </div>
    </el-dialog>
  </div>
</template>
<script>

import { AIMarker } from 'vue-picture-bd-marker'
import axios from 'axios';
import Cookies from "js-cookie"
import VueUploadComponent from 'vue-upload-component';
import Draggable from 'vue-draggable-float'
//引入组件库



export default {
  name: 'stagePicPage',
  components: { 
    'ui-marker': AIMarker,
    'file-upload': VueUploadComponent,
    // 'Suspend': Suspend,
    Draggable,
 },
  data() {
    return {
      modified: false,
      already: false,
      rightDistance: 0,
      bottomDistance: 0,
      loading_src: 'https://image.uisdc.com/wp-content/uploads/2015/05/load20150504-5.gif',
      already_src: 'https://trademark.zbjimg.com/pattern-prod/2017/image_53/27078207.jpg',

      highlight_id: 0,
      // uuid的作用是用来区分每一张不同的图片，因为框选标注的插件需要
      // uuid: '0da9130',
      // filelist的作用是暂时存储我们要增添的图片，以便后端进行提交
      selectedFile: null,
      //currentInfo是当前正在进行标注的图片信息
      currentInfo: {
        currentBaseImage:// 当前标注图像的地址
          'https://image.uisdc.com/wp-content/uploads/2015/05/load20150504-5.gif',
        rawW: 1200,//当前标注图像的原始宽度、高度
        rawH: 828,
        currentW: 1134,//当前标注图像在标注区压缩后的宽度、高度
        currentH: 632,
        uuid: '',//与上面的uuid其实是同一个东西
        // checked: false, // false表示当前图片还没有标记过

        /*data是所有标注框信息的列表，id:标注框的id，实际产生我是通过getDate()获得的唯一数字，但在读取coco.json时忘记有没有这项了，没有就要自己加上唯一的id
        tag_id是标签对应的id，tag_name标签名，剩下的是标注框的中心点坐标、宽高
        data从pics中初始化，更新时先更新data，然后更新回pics，再传回后端*/
        data: [
          // {
          //   id: 1,
          //   tag_id: 1,
          //   tag_name: "diaose",
          //   x_ul: 100,
          //   y_ul: 200,
          //   wid: 50,
          //   hei: 50
          // },
        ] // 表示图片矩形标记信息
      },
      // pics是所有的图片信息，我们需要在增删图片、修改标注时维护这部分内容，初始时通过后端接口获得这部分内容，但其实仅修改标注时不维护，直接将修改的信息上传后端就行，待定
      // 同时，这部分的初始化是通过读取整个annotation文件得到的，annotation里面不止这几个项，其余的项我的想法是放在与下面pics平行的位置，用一个rest来暂存多余内容，在我们修改完标注后结合pics和data
      pics: [
        // {
        //   cropImage: 'https://seopic.699pic.com/photo/50041/3365.jpg_wh1200.jpg',
        //   annotations: [
        //     { id: 1, catagory_id: 0, bbox: [11, 22, 10, 5] },
        //     { id: 2, catagory_id: 1, bbox: [35, 44, 20, 14] }
        //   ]
        // },
      ],
      altURL: 'https://img-qn.51miz.com/2018/02/08/06/2018020806948082_P1330830_60ced2dfO.jpg',
      active: 0, // 当前图片序号
      picTotal: 10, // 照片总数，需要在初始时进行加载

      // 所有的标签名及其id
      tags: [
        // {
        //   tagName: '缺陷',
        //   tag: '0x0001'
        // },
      ],

      //下面的几个内容不用管，都是插件使用的部分
      allInfo: [], // 图片的矩形标记信息集合
      imageInfo: [], // 存储图片原始信息

      innerVisible: false,
      innerForm: {
        tagName: '',
        tag: ''
      },

      tep_rules: {
        tagName: [{ required: true, message: '请输入', trigger: 'blur' }],
        tag: [{ required: true, message: '请输入', trigger: 'blur' }]
      }
    }
  },
  computed:{
    
  },
  created() {
    this.init_pics()
  },
  mounted() {
    window.addEventListener("beforeunload", this.leaveconfirm, false)
    const screenWidth = window.innerWidth;
    const screenHeight = window.innerHeight;
    // 计算距离右边整个屏幕宽度的80%的距离
    this.rightDistance = screenWidth * 0.65;
    // 计算距离底部整个屏幕高度的10%的距离
    this.bottomDistance = screenHeight * 0.08;
  },

  beforeDestroy(){
    window.addEventListener("beforeunload", this.leaveconfirm, false)
  },
  beforeRouteLeave(to, from, next) {
    if (this.modified) { // 此处为个人项目条件判断，当条件成立时才执行路由守卫
      this.$confirm('当前信息未保存，离开页面将会放弃所有修改数据，', '提示', {
        closeOnClickModal: false,
        confirmButtonText: '保存',
        cancelButtonText: '保存',
        type: 'warning'
      }).then(() => {
      	// 点击确定则往下执行
        //this.saveAll()
        next()
      }).catch(() => {
		// 取消则关闭弹窗不执行
	  })
    } else {
      // 条件不成立则继续往下执行
      next()
    }
  },
  methods: {
    leaveconfirm(event){
      if (this.modified) {
        event.preventDefault()
        event.returnValue = '您在页面编辑了未保存，是否确认离开'
        return '您在页面编辑了未保存，是否确认离开'
      }
    },
    handleFileInputClick() {
      this.$refs.fileInput.click(); // 触发文件选择输入框的点击事件
    },
    saveAll(){
      const formData = new FormData();
      axios.post('http://127.0.0.1:5000/Dataset/save', formData,{
        headers: { 'Authorization': 'Bearer ' + Cookies.get('token')},
      }).then(res=>{
        console.log('保存所有信息到后端')
        this.modified = false
        this.$router.push('/user')
      }).catch(error=>{
        console.log('保存所有信息失败',error);
        return null;
      })
    },
    saveAnno(){
      const formData = new FormData();
      formData.append("image_id", this.currentInfo.uuid);
      var list = [];
      for(let i =0;i<this.currentInfo.data.length;i++)
      {
        var box = [];
        box.push(this.currentInfo.data[i].x_ul);
        box.push(this.currentInfo.data[i].y_ul);
        box.push(this.currentInfo.data[i].wid);
        box.push(this.currentInfo.data[i].hei);
        let obj = {
          area: this.currentInfo.data[i].area,
          iscrowd: this.currentInfo.data[i].iscrowd,
          image_id: this.currentInfo.uuid,
          bbox: box,
          category_id: this.currentInfo.data[i].tag_id,
          id: this.currentInfo.data[i].id,
          ignore: this.currentInfo.data[i].ignore,
          segmentation: this.currentInfo.data[i].segmentation,
        };
        list.push(obj);
      }
      formData.append("annotations", JSON.stringify(list));
      axios.post("http://127.0.0.1:5000/Dataset/workspace/modify-annotation",formData,{
        headers: { 'Authorization': 'Bearer ' + Cookies.get('token')},
      }).then(res=>{
        console.log("保存所有标注信息到后端成功")
        this.modified = true;
      }).catch(error=>{
        console.log("保存所有标注信息到后端失败", error);
        return null;
      });
    },

    handleFileChange(event) {
      this.selectedFile = event.target.files[0];
    },
    // 上传文件
    uploadFile() {
      const formData = new FormData();
      formData.append('proc_type', 'add');
      formData.append('data_type', 'image');
      formData.append('image', this.selectedFile);

      // 使用 axios 或其他 HTTP 客户端库发送 POST 请求到后端
      // 你需要替换下面的 URL 为后端接收上传的 API 端点
      axios.post('http://127.0.0.1:5000/Dataset/workspace/modify', formData, {
        headers: {
          'Authorization': 'Bearer ' + Cookies.get('token'),
          'Content-Type': 'multipart/form-data',
        },
      })
      .then(response => {
        // 处理成功上传后的响应
        console.log('上传成功', response.data);
        var id_new = response.data.image_id;
        let url_new = "http://127.0.0.1:5000/Dataset/workspace/image/" + id_new;
        axios.get(url_new, {
          headers: {
            'Authorization': 'Bearer ' + Cookies.get('token'),
          },
          responseType: 'blob',
        }).then(res=>{
          let blob = new Blob([res.data]);
          console.log(blob, "BLOB")
          let image_url = URL.createObjectURL(blob);
          this.pics.push({
            id: id_new,
            url: image_url
          })
          console.log("更新pics成功")
          this.modified = true;
        }).catch(error => {
            console.log("更新pics出错", error);
            return null;
          });
      }).catch(error => {
        // 处理上传失败的情况
        console.error('上传失败', error);
      });
    },

    init_pics(){
      axios.get('http://127.0.0.1:5000/Dataset/workspace', {
        headers: {
          'Authorization': 'Bearer ' + Cookies.get('token'),
        }
      }).then(res => {
        console.log(res, "相应信息")
        //需要更新的信息有：pics，active，picTotal，tags
        this.picTotal = res.data.image_count;
        console.log(this.picTotal, "图片总数");
        this.active = 0;
        var id_list = res.data.image_ids;
        console.log(id_list, "id列表");
        const baseurl = "http://127.0.0.1:5000/Dataset/workspace/image/";
        var urlset = id_list.map((number) => {
          return baseurl + number;
        });
        let cate = res.data.categories;
        for(let i=0; i<cate.length;i++)
        {
          var item = cate[i];
          var newTag = {
            tagName: item.name,
            tag: item.id
          };
          this.tags.push(newTag)
        }
        

        // 使用Promise.all来等待所有图像请求完成
        Promise.all(urlset.map(url => {
          return axios.get(url, {
            headers: {
              'Authorization': 'Bearer ' + Cookies.get('token'),
            },
            responseType: 'blob',
          }).then(res => {
            let blob = new Blob([res.data]);
            console.log(blob, "BLOB")
            let image_url = URL.createObjectURL(blob);
            console.log(image_url, "IMAGE_URL")
            return image_url;
          }).catch(error => {
            console.log("获取图片出错", error);
            return null;
          });
        })).then(imgUrls => {
          // imgUrls数组中包含了所有图像的URL，按照顺序与id_list对应
          for (let i = 0; i < id_list.length; i++) {
            let id_ = id_list[i];
            let url_ = imgUrls[i];
            let obj = { id: id_, url: url_ }
            this.pics.push(obj);
          }
          this.currentInfo.currentBaseImage=this.already_src
          console.log(this.pics, "pics");
        });
      });
    },
    highlight(id) {
      var canvas = document.getElementById("highlighted")
      var ctx = canvas.getContext("2d")
      console.log("hightlight", id)
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      for (const box of this.currentInfo.data){
        if (box.id === id){
          ctx.strokeStyle = 'yellow'
          ctx.lineWidth = 4
          console.log(box.x_ul, box.y_ul, box.wid, box.hei)
          ctx.strokeRect(box.x_ul, box.y_ul, box.wid, box.hei)
          this.highlight_id = id
        }
      }
    },
    
    //canvas基础的画框操作
    drawBoxes() {
      var canvas = document.getElementById("anno_canvas")
      var ctx = canvas.getContext("2d")
      console.log("drawBoxes")
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      for (const box of this.currentInfo.data) {
        ctx.strokeStyle = 'red'
        ctx.lineWidth = 2
        console.log(box.x_ul, box.y_ul, box.wid, box.hei)
        ctx.strokeRect(box.x_ul, box.y_ul, box.wid, box.hei)
      }
      console.log(this.currentInfo.data)
    },
    //标注框的删除函数
    del_anno(id) {
      this.currentInfo.data = this.currentInfo.data.filter(item => item.id !== id)
      if(this.highlight_id === id){
        var canvas = document.getElementById("highlighted")
        var ctx = canvas.getContext("2d")
        ctx.clearRect(0, 0, canvas.width, canvas.height);
      }
      this.drawBoxes()
      this.modified = true;
    },

    //-----------------------------------------------------------------------------这部分为插件所需要的函数---------------------------------------------------------------------
    /**记录图片当前的大小和原始大小 data={rawW,rawH,currentW,currentH} */
    onImageLoad(data) {
      console.log(data)
      this.imageInfo = data
    },
    // 当控件准备完成后回调，参数为 uniqueKey
    onReady() {
      console.log("onready")
      // let markerDiv = document.getElementsByClassName('vmr-ai-panel')
      // let innnerDiv = markerDiv[0].firstChild
      // let markerImg = document.getElementsByClassName('vmr-ai-raw-image')
      // let markerMask = document.getElementsByClassName('vmr-ai-raw-image-mask')
      // markerDiv[0].setAttribute('style', 'position: relative; overflow: hidden; width: 60%; height: 60%;')
      // innnerDiv.setAttribute('style', 'position: relative; overflow: hidden;')
      // markerImg[0].setAttribute('style', 'display: block; position: absolute; user-select: none; width:700px; height: 500px;')
      // markerMask[0].setAttribute('style', 'user-select: none; position: absolute; cursor: crosshair; left: 0px; top: 0px;width:700px; height: 500px;')
    },
    /**
   * 画框后回调,data 和 uniqueKey先不用了
   */
    onDrawOne(data, uniqueKey) {
      if (!this.selected.name || !this.selected.value) {
        this.$message.info('请先设置标签')
        this.$refs['aiPanel-editor'].getMarker().clearData()
        return
      }
      let name = data.tagName === '请选择或添加新标签' ? this.selected.name : data.tagName
      let tagValue = data.tagName === '请选择或添加新标签' ? this.selected.value : data.tag
      this.$refs['aiPanel-editor'].getMarker().setTag({
        tagName: name,
        tag: tagValue
      })
      console.log("onDrawOne", uniqueKey)
    },
    /**
     * 当选中图片上的标注框时回调，参数为data【标注数据】, uniqueKey
     */
    selectOne(uniqueKey) {
      console.log("selectOne", uniqueKey, this.data)
    },
    /**
     * 当标注框位置或者标框属性发生改动时回调，参数为data【标注数据】, uniqueKey
     */
    onUpdated(data, uniqueKey) {
      console.log("onUpdated", uniqueKey, data)
    },

    setTag(v) {
      this.$refs['aiPanel-editor'].getMarker().setTag(v)
    },
    addTag() {
      this.innerVisible = true
      this.innerForm.tagName = ''
      this.innerForm.tag = ''
    },
    delTag(index, tag_id) {
      this.tags.splice(index, 1);
      const formData = new FormData();
      formData.append('proc_type', 'delete');
      formData.append('data_type', 'category');
      formData.append('id', tag_id);
      // 使用 axios 或其他 HTTP 客户端库发送 POST 请求到后端
      // 你需要替换下面的 URL 为后端接收上传的 API 端点
      axios.post('http://127.0.0.1:5000/Dataset/workspace/modify', formData, {
        headers: {
          'Authorization': 'Bearer ' + Cookies.get('token'),
        },
      })
      .then(response => {
        // 处理成功上传后的响应
        console.log('删除成功', response.data);
        this.modified = true;
      })
      .catch(error => {
        // 处理上传失败的情况
        console.error('删除失败', error);
      });
      
    },
    close() {
      this.innerVisible = false
      this.$refs['innerForm'].resetFields()
    },
    beforeClose(done) {
      this.$refs['innerForm'].resetFields()
      done()
    },
    //-----------------------------------------------------------------------------这部分为插件所需要的函数---------------------------------------------------------------------

    // 添加标签的函数
    createForm(formName) {
      this.$refs[formName].validate(valid => {
        if (valid) {
          for (let index in this.tags) {
            let item = this.tags[index]
            if (
              item.tagName === this.innerForm.tagName
              // || item.tag === this.innerForm.tag
            ) {
              this.$message.warning('标签名已存在，请重新输入')
              return
            }
          }

          const formData = new FormData();
          formData.append('proc_type', 'add');
          formData.append('data_type', 'category');
          let obj = {
            supercategory: "none",
            id: 0,
            name: this.innerForm.tagName,
          }

          formData.append('category', JSON.stringify(obj));
          console.log(formData, "传入表单数据");

          // 使用 axios 或其他 HTTP 客户端库发送 POST 请求到后端
          // 你需要替换下面的 URL 为后端接收上传的 API 端点
          axios.post('http://127.0.0.1:5000/Dataset/workspace/modify', formData, {
            headers: {
              'Authorization': 'Bearer ' + Cookies.get('token'),
            },
          })
          .then(response => {
            // 处理成功上传后的响应
            console.log('新增成功', response.data);
            this.innerForm.tag = response.data.category_id;
            this.tags.push({
              tagName: this.innerForm.tagName,
              tag: this.innerForm.tag
            });
            this.modified = true;
          })
          .catch(error => {
            // 处理上传失败的情况
            console.error('新增失败', error);
          });
          
          this.innerVisible = false
        }
      })
    },

    //完成标记，提交标记集合，目前仅提交到data，未更新至pics乃至后端
    submitForm() {
      console.log(this.$refs['aiPanel-editor'])
      let data = this.$refs['aiPanel-editor'].getMarker().getData()

      this.allInfo = data
      console.log(this.allInfo)

      let size = {
        width: this.imageInfo.rawW,
        height: this.imageInfo.rawH
      }
      console.log(size.width, size.height)
      console.log(this.currentW, this.currentH)

      let x_ul = Math.round(((parseFloat(this.allInfo[0].position.x.substring(0, this.allInfo[0].position.x.length - 1)) * size.width) / 100))
      let y_ul = Math.round(((parseFloat(this.allInfo[0].position.y.substring(0, this.allInfo[0].position.y.length - 1)) * size.height) / 100))
      console.log('左上角点坐标', "(", x_ul, y_ul, ")")
      let width = Math.round((((parseFloat(this.allInfo[0].position.x1.substring(0, this.allInfo[0].position.x1.length - 1)) - parseFloat(this.allInfo[0].position.x.substring(0, this.allInfo[0].position.x.length - 1))) * size.width) / 100))
      let height = Math.round((((parseFloat(this.allInfo[0].position.y1.substring(0, this.allInfo[0].position.y1.length - 1)) - parseFloat(this.allInfo[0].position.y.substring(0, this.allInfo[0].position.y.length - 1))) * size.height) / 100))
      console.log(width, height, "宽度x高度")
      let newObj = {
        id: new Date().getTime(),
        tag_id: this.allInfo[0].tag,
        tag_name: this.allInfo[0].tagName,
        x_ul: x_ul,
        y_ul: y_ul,
        wid: width,
        hei: height,
        area: width*height,
        iscrowd: 0,
        ignore: 0,
        segmentation: [],
      }
      this.currentInfo.data.push(newObj)
      // 将提交的标注框进行删除
      console.log(this.currentInfo.data)
      this.$refs['aiPanel-editor'].getMarker().clearData()
      console.log(this.currentInfo.data)
      this.drawBoxes()
      this.modified = true;
    },

    // 点击左右按钮显示更多
    showMore(v) {
      let el = this.$refs.picContainer
      // let percent = (this.active / this.pics.length) * 100
      if (v == 'up') {
        this.active++
        if (this.active >= this.picTotal - 3) {
          // 最后4张图
          this.active = this.pics.length - 3
          return
        }
        if (
          this.pics.length - 3 == this.active &&
          this.pics.length < this.picTotal
        ) {
          this.photoPageIndex++
          this.getPhotos()
          return
        }
      } else {
        this.active--
        if (this.active < 0) this.active = 0
      }
      el.style.transform =
        'translateX(-' + (this.active / this.pics.length) * 100 + '%)'
    },
    //搭配showmore展示所有图片
    getPhotos() {
      this.$nextTick(() => {
        let el = this.$refs.picContainer
        if (el) {
          el.style.width = el.scrollWidth + 'px'

          el.style.transform =
            'translateX(-' + (this.active / this.pics.length) * 100 + '%)'
        }
      })
    },

    /**得到当前点击图片，将信息更新到currentInfo*/

    activePic(v, currentIndex, arrayId) {
      // 写回data
      if(this.currentInfo.currentBaseImage != v)
      {
        var canvas = document.getElementById("highlighted")
        var ctx = canvas.getContext("2d")
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        this.currentInfo.data = []
        this.currentInfo.currentBaseImage = v
        this.active = arrayId
        // const fileExtension = '.jpg_wh1200.jpg'
        // const extensionIndex = this.currentInfo.currentBaseImage.lastIndexOf(fileExtension)

        // if (extensionIndex !== -1) {
        //   const startIndex = Math.max(extensionIndex - 5, 0)
        //   this.currentInfo.uuid = this.currentInfo.currentBaseImage.slice(startIndex, extensionIndex)
        // }
        this.currentInfo.uuid = currentIndex
        console.log(this.currentInfo.uuid, "图片编号")
        // 获取图片的原始宽高
        let attr_url = 'http://127.0.0.1:5000/Dataset/workspace/image-attribute/' + this.currentInfo.uuid
        console.log(attr_url, "访问属性的url")
        axios.get(attr_url, {
          headers: {
            'Authorization': 'Bearer ' + Cookies.get('token'),
          }
        }).then(res =>{
          this.currentInfo.rawH = res.data.image_attribute.height
          this.currentInfo.rawW = res.data.image_attribute.width
        }).catch(error=>{
          console.log(error, "获取图片长宽失败")
          return null
        })
        console.log(this.currentInfo)
        // console.log(this.currentInfo.uuid)

        let anno_url = 'http://127.0.0.1:5000/Dataset/workspace/annotation/' + this.currentInfo.uuid
        axios.get(anno_url, {
          headers: {
            'Authorization': 'Bearer ' + Cookies.get('token'),
          }
        }).then(res =>{
          console.log(res.data.annotations, "标注信息");
          for(let i=0; i<res.data.annotations.length;i++)
          {
            let item = res.data.annotations[i];
            // console.log(item,"项目")
            var name = "";
            // console.log(this.tags, "全部标签")
            for(let j=0;j<this.tags.length;j++)
            {
              if(this.tags[j].tag == item.category_id)
              {
                name = this.tags[j].tagName;
                break;
              }
            };
            let newAnno = {
              id: item.id,
              tag_id: item.category_id,
              tag_name: name,
              x_ul: item.bbox[0],
              y_ul: item.bbox[1],
              wid: item.bbox[2],
              hei: item.bbox[3],
              area: item.area,
              iscrowd: item.iscrowd,
              ignore: item.ignore,
              segmentation: item.segmentation
            };
            this.currentInfo.data.push(newAnno);
          }
          console.log(this.currentInfo.data, "后端导入数据集成功")
          this.drawBoxes();
        }).catch(error=>{
          console.log(error, "获取图片标注信息失败")
          return null
        })
      }
      
      
    },

    // handleChange(label) {
    //   console.log(label)
    // },

    // 此处要有删除图片的操作实现
    delPic() {
      if (this.active < 0) {
        alert('请先选择一张图片再进行删除')
      }
      else {
        this.pics.splice(this.active, 1)
        this.active = -1
        this.currentInfo.currentBaseImage = this.altURL
        //发信号给后端
        const formData = new FormData();
        formData.append('proc_type', 'delete');
        formData.append('data_type', 'image');
        formData.append('id', this.currentInfo.uuid);

        // 使用 axios 或其他 HTTP 客户端库发送 POST 请求到后端
        // 你需要替换下面的 URL 为后端接收上传的 API 端点
        axios.post('http://127.0.0.1:5000/Dataset/workspace/modify', formData, {
          headers: {
            'Authorization': 'Bearer ' + Cookies.get('token'),
          },
        })
        .then(response => {
          // 处理成功上传后的响应
          console.log('删除成功', response.data);
          this.modified = true;
        })
        .catch(error => {
          // 处理上传失败的情况
          console.error('删除失败', error);
        });

      }
    }
  }
}
</script>
  
<style lang="scss" scoped>
.pics {
  position: relative;
  width: 100%;
  height: 10%;
  overflow: hidden;
  margin-bottom: 20px;
  display: flex;
  justify-content: center;
  align-items: center;

  .arrow {
    width: 20px;
    height: 20px;
    border-radius: 50%;
    background-image: url('@/assets/images/left_arrow.jpg');
    background-repeat: no-repeat;
    background-size: contain;

    &.arrow-right {
      transform: rotate(180deg);
    }
  }

  .pic-container {
    width: calc(100% - 30px);
    height: 100%;
    margin: 0 auto;
    overflow: hidden;

    .pic-box {
      height: 100%;
      // min-width: 1180px;
      min-width: calc(100% - 30px);
      transition: all 0.5s linear;
      display: flex;
      flex-wrap: nowrap;
    }

    .pic {
      float: left;
      border: 1px solid #ccc;
      box-sizing: border-box;
      margin-right: 10px;
      width: 185px;
      height: 114px;

      .info {
        width: 183px;
        height: 100%;
        background-size: 100%;
        background-repeat: no-repeat;
        background-position: center;
        position: relative;

        &:hover {
          border: 1px solid skyblue;
        }
      }
    }
  }
}

.height-control {
    // width: 1180px;
    position: relative;
    width: calc(100% - 30px);
    height: 80%;
    margin: 0 auto;
    overflow: hidden;}


.save-button{
  width:100%;
  margin-bottom:10px
}
.tagList {
  margin-bottom: 20px;
  display: flex;
  flex-wrap: wrap;

  .title {
    text-align: center;
    font-weight: bold;
  }

  .handleButton {
    width: 100%;
    margin-bottom: 10px;
  }

  .tags {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 10px 0;

    .el-icon-delete {
      cursor: pointer;
    }
  }

  .annos {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 10px 0;

    .el-icon-delete {
      cursor: pointer;
    }
  }
}

.img-container {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: flex-start;
  justify-content: center;
  position: relative;
}

// .image-wrapper {
//   position: absolute;
//   top: 0;
//   left: 0;
//   width: 100%;
//   height: 100%;
// }

.limited-image,
#anno_canvas,
#highlighted {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  /* 设置宽度为100%以适应父元素 */
  object-fit: contain;
}

.vertical-button
{
  margin: 5px;
}
.custom-container {
  background-color: #f0f0f0; /* 设置背景色为浅灰色 */
  border: 1px solid #ccc; /* 添加1像素的灰色边框 */
  // padding: 10px; /* 可选：添加内边距以增加边框和内容之间的间距 */
}


</style>
  
  