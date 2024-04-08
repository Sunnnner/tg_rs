<template>
  <el-form :model="form" label-width="auto" style="max-width: 600px">
    <el-form-item label="python">
      <el-input v-model="form.python" @click="getPython" placeholder="请选择虚拟环境python"/>
    </el-form-item>
    <el-form-item label="api id">
      <el-input v-model="form.api_id"/>
    </el-form-item>
    <el-form-item label="api hash">
      <el-input v-model="form.api_hash"/>
    </el-form-item>
    <el-form-item label="api session">
      <el-input v-model="form.session"/>
    </el-form-item>
    <el-form-item label="proxy host">
      <el-input v-model="form.proxy_host" placeholder="默认为127.0.0.1"/>
    </el-form-item>
    <el-form-item label="proxy port">
      <el-input v-model="form.proxy_port" placeholder="默认为6153"/>
    </el-form-item>
    <el-form-item>
      <el-button type="primary" @click="saveConfig">保存配置文件</el-button>
      <el-button type="primary" @click="onSubmit">运行</el-button>
    </el-form-item>
  </el-form>

</template>

<script lang="ts" setup>
import {onMounted, reactive} from "vue";
import {dialog} from '@tauri-apps/api';
import {invoke} from '@tauri-apps/api/tauri';
import store from "./storage_store";
// do not use same name with ref
let form: any = reactive({
  python: "",
  api_id: "",
  api_hash: "",
  session: "",
  proxy_host: "",
  proxy_port: "",
});

const getPython = async () => {
  const result = await dialog.open({
    multiple: false,
    directory: false,
  });
  if (typeof result === "string") {
    form.python = result;
  }
};

const saveConfig = () => {
  store.set("config", form);
  store.save();
};

const onSubmit = () => {
  invoke('run_python_script', {
    python: form.python,
    apiId: form.api_id,
    apiHash: form.api_hash,
    proxyHost: form.proxy_host || "127.0.0.1",
    proxyPort: form.proxy_port || "6153",
    session: form.session,
  })
}

const loadConfig = () => {
  store.get("config").then((res: any) => {
    if (res) {
      form.python = res.python;
      form.api_id = res.api_id;
      form.api_hash = res.api_hash;
      form.session = res.session;
      form.proxy_host = res.proxy_host;
      form.proxy_port = res.proxy_port;
    }
  });
};

// 加载的时候load配置文件
onMounted(() => {
  loadConfig();
})

</script>
