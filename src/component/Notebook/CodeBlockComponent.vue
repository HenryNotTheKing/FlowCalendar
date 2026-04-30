<template>
  <node-view-wrapper class="code-block">
    <el-select v-model="selectedLanguage" placeholder="选择语言" size="small" style="position: absolute; right: 0.5rem; top: 0.5rem; width: 120px;">
      <el-option label="auto" :value="null"></el-option>
      <el-option v-for="(language, index) in languages" :key="index" :label="language" :value="language"></el-option>
    </el-select>
    <pre><code ref="codeElement"><node-view-content /></code></pre>
  </node-view-wrapper>
</template>


<script>
import { NodeViewContent, nodeViewProps, NodeViewWrapper } from '@tiptap/vue-3'

export default {
  components: {
    NodeViewWrapper,
    NodeViewContent,
  },

  props: nodeViewProps,

  data() {
    return {
      languages: this.extension.options.lowlight.listLanguages(),
    }
  },

  computed: {
    selectedLanguage: {
      get() {
        return this.node.attrs.language
      },
      set(language) {
        this.updateAttributes({ language })
      },
    },
  },
}
</script>

<style lang="scss">
.tiptap {
  .code-block {
    position: relative;

    .el-select {
      position: absolute;
      right: 0.5rem;
      top: 0.5rem;
    }
  }
}

[data-theme="dark"] .tiptap .code-block pre {
  background-color: #2d2d2d;
  color: #f8f8f2;
}

[data-theme="dark"] .tiptap .code-block .el-select {
  background-color: #3a3a3a;
  border-color: #555;
}

[data-theme="dark"] .tiptap .code-block .el-select .el-input__inner {
  background-color: #3a3a3a;
  color: #f8f8f2;
  border-color: #555;
}

[data-theme="dark"] .tiptap .code-block .el-select .el-input__inner:focus {
  border-color: #007acc;
}

[data-theme="dark"] .tiptap .code-block .el-select .el-input__inner:hover {
  border-color: #007acc;
}
</style>