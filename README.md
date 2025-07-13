# MCP-PDF-Parser

## 任务描述
PDF 文档解析器是一个功能强大的工具，其核心任务是将包含复杂格式和排版的 PDF 文件内容，高效且准确地解析并转换为结构清晰、易于编辑和版本控制的 Markdown 格式文本。该解析器需要深入处理 PDF 的内部结构，包括文本流、字体信息、布局元素等，以生成语义正确、格式规范的 Markdown 输出。

## 任务范围
该解析器的开发任务涵盖了从 PDF 文件输入到最终 Markdown 输出的完整处理流程。具体包括但不限于：设计并实现高效的 PDF 文件内容读取与解码机制；开发能够识别并转换 PDF 中文本、基本排版（如标题、列表）、表格（如可能）等元素为对应 Markdown 语法的核心转换引擎；提供灵活的输出配置选项以满足不同场景需求；确保解析过程对常见 PDF 特性（如嵌入字体、多语言编码）的兼容性；以及设计健壮的错误处理机制以应对格式异常或损坏的 PDF 文件。


## 详细步骤
> 该步骤仅供参考，学生可自行发挥想象空间，探索更优化的算法或更丰富的功能特性。
PDF 解析器旨在提供强大而灵活的解析能力，其核心特点包括：
- 支持基本的 PDF 文本提取：能够精确识别并提取 PDF 文档中的文本内容流，包括处理复杂的文本布局（如分栏、环绕）、处理内联图像或图形元素中的替代文本（Alt Text），并尽可能保留原始文本的语义顺序和逻辑结构。
- 可以选择按页面分割文档：提供可配置的选项，允许用户决定是否在生成的 Markdown 输出中依据原始 PDF 的页面边界进行内容分割。用户可选择在每个页面内容之间插入明确的分页符标记（如 --- 或自定义分隔符），或者选择生成一个连续的、无显式分页的 Markdown 文档，便于不同场景下的内容整合与处理。
- 自动处理 PDF 字体和编码：内置智能机制，能够自动识别 PDF 文件中使用的各种字体（包括标准字体和嵌入字体）以及复杂的字符编码方案（如 Unicode, ANSI, 或特定于语言的编码）。解析器会进行必要的字符映射和解码转换，确保提取出的文本能够正确无误地以 UTF-8 等通用编码呈现，避免乱码问题，并尽可能还原特殊字符和符号。
- 支持多页面 PDF 文档：具备高效处理包含大量页面（数十页甚至数百页）的 PDF 文档的能力。解析过程应具备良好的内存管理和性能优化，能够稳定、流畅地处理长文档，确保最终生成的 Markdown 文件完整包含所有页面的内容，且结构清晰有序。


# 📄 MCP-PDF-Parser
基于 PyMuPDF（fitz） 的 高级 PDF 转 Markdown 解析器，支持：  
✅ 自动提取文字（保持基本结构与层次）  
✅ 自动检测并插入图片（提取 PDF 内嵌图片，自动插入到 Markdown）  
✅ 识别数学符号并保留（可直接复制到 Word / Typora 渲染）  
✅ 标题层次解析（基于字体大小自动推断标题等级）  
✅ 按页拆分（可选）  
✅ 可选分页分隔符  
✅ Unicode、NFKC 标准化处理  

# ⚙️ 项目结构

MCP-PDF-PARSER/   
└── test file/  
    ├── test.pdf  
    ├── pdf_parser.py  
    └── README.md  
  
# 🚀 使用方法

## 1. 安装依赖

```
pip install PyMuPDF
```

## 2. 基本命令

### (1)最基本无参数命令

```
python pdf_parser.py <input_pdf_path> <output_md_path>
```

### (2)使用 --split（按页拆分输出

```
python pdf_parser.py "D:\Docs\sample.pdf" "D:\Docs\sample.md" --split
```

在生成的 sample.md 中，每页之间会插入默认分页分隔符：

```
---
```
### (3)使用 --split 并自定义分页分隔符
若需要自定义分页分隔符（例如 *** PAGE BREAK ***），可使用：

```
python pdf_parser.py "D:\Docs\sample.pdf" "D:\Docs\sample.md" --split --page-separator "*** PAGE BREAK ***"
```

在生成的 sample.md 中，每页之间会插入：

```
*** PAGE BREAK ***
```


## 3.执行效果 
执行后将在指定位置生成：

转换后的 Markdown 文件（包含提取的文字和图片引用）

同目录下自动创建 <output_name>_images 文件夹，存放提取的图片

## 4.参数说明

| 参数                             | 说明                                     |
| ------------------------------ | -------------------------------------- |
| `input_pdf`                    | 输入 PDF 文件路径                            |
| `output_md`                    | 输出 Markdown 文件路径                       |
| `--split`                      | （可选）启用按页拆分输出，便于分段管理                    |
| `--no-split`                   | （可选）禁用按页拆分（默认）                         |
| `--page-separator <separator>` | （可选）当启用 `--split` 时，自定义分页分隔符，默认为 `---` |

## 5.效果测试

### 1️⃣ 克隆仓库到本地

```
git clone https://github.com/Ryanjxy123/MCP-PDF-Parser.git
cd MCP-PDF-Parser
```
### 2️⃣ 安装依赖

```
pip install PyMuPDF
```


### 3️⃣ 执行命令

```
python .\pdf_parser.py "test file\test.pdf" output.md
```

## 🙏 致谢

感谢你使用 **MCP-PDF-Parser**。