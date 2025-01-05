支持的Hugo主题

- [Fixit](https://fixit.lruihao.cn/zh-cn/)

## TODO List

- [x] 全新的命令行工具`ob2hugo`来实现将Obsidian markdown 转换到 Hugo markdown， 并将文件放在指定的目录下，目前仅支持Fixit主题。
- [x] 通过配置文件来控制ob2hugo的行为
- [x] 可以使用`include_files`和`exclude_files`来控制哪些文件被转换，哪些文件不被转换。
- [x] 通过读取obsdian md文件front yaml中的publis来控制哪些文章被转换
- [x] 使用`author`来控制文章的作者，而不是使用Front Matter中的author。
- [x] 可以控制是否生成目录时清空原来的hugo content和assets目录
- [x] ~~如果文章没有设置draft的话，则为其设置默认值，这个默认值可以在配置文件中设置。~~
- [x] 支持转换yaml front matter
- [x] 支持转换math equation block
- [x] 支持转换inline math equation
- [x] 支持转换图片链接，并将对应图片转移到hugo assets目录下
- [x] 支持移除Excalidraw所产生的注释（该注释时用于链接原始Excalidraw文件，用来进行编辑的）
- [ ] 支持转换math theorem callout block
- [ ] 支持转换obsidian的双链引用，使用ref shortcode实现
- [ ] 支持转换equation, theorem, callout block的引用
- [ ] 支持dataview的转换
- [x] 在hugo目录中保持ob中的目录结构
- [ ] 在front matter中加入categories和collection分类法
- [ ] 将所有的callout转变成fixit的Admonition shortcode，这样便于去和其他格式转换解耦
- [x] 使用[kroki](https://kroki.io/)支持Excalidraw
- [ ] 更加清晰的log
- [ ] 在文章的最后添加反向引用列表
- [ ] **一个新的实现思路，先将整个文档按照obsidian markdown的语法解析成AST，然后再将该AST渲染成hugo markdown的格式。可以参考[mistune](https://github.com/lepture/mistune)的实现，或者直接使用它。**

## 支持Obsidian中嵌入的Excalidraw

需要安装[kroki](https://kroki.io/)，详细安装方式请见[kroki installation](https://kroki.hugomods.com/docs/installation/)。
