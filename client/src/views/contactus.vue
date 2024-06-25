<template>
    <div class="container">
        <div class="content">
            <h1>联系我们</h1>
            <h2>qq: 3318835912</h2>
            <h3>邮箱: zhongmh26@mail2.sysu.edu.cn</h3>
        </div>
    </div>
</template>

<script>
export default {
    data() {
        return {}
    }
}
</script>

<style scoped>
.container {
    display: flex;
    justify-content: center;
    align-items: center;
    height: 100vh;
    text-align: center;
    background-color: #ffffff; /* 背景颜色设置为白色 */
}

.content {
    padding: 20px;
    border: 2px solid #e0e0e0;
    border-radius: 10px;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    background-color: #ffffff; /* 内容容器背景颜色设置为白色 */
}

h1, h2, h3 {
    margin: 10px 0;
    font-family: 'Arial', sans-serif;
    color: #000000; /* 字体颜色设置为黑色 */
}

h1 {
    font-size: 2.5rem;
}

h2 {
    font-size: 1.5rem;
}

h3 {
    font-size: 1.2rem;
}
</style>
