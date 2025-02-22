import os
import shutil
import datetime
import markdown
import yaml
from jinja2 import Environment, FileSystemLoader
from PyPDF2 import PdfReader
from markdown.extensions.toc import TocExtension
from bs4 import BeautifulSoup
import re

# 配置
CONFIG = {
    'site_name': 'uuku\'s blog',
    'author': 'uuku',
    'keywords': ['算法竞赛', '数学', 'AI', '学习笔记', 'Latex'],
    'description': 'Personal Blog System',
    'local_url': 'http://127.0.0.1:8080',
    'public_url': 'https://blog.nan2inf.com',
    'theme': 'default',
    'output_dir': '',
    'source_dir': './content',
    'templates_dir': './templates',
    'static_dir': './static',
    'per_page': 10,
    'categories': ['算法竞赛', '数学', 'AI', '学习笔记', 'Latex'],
    'extensions': ['md', 'pdf', 'html'],
    'tag_count': 5,  # 侧边栏标签数量, 显示最多的tag_count个标签
}

# 初始化Jinja2环境
env = Environment(loader=FileSystemLoader(CONFIG['templates_dir']))

class Post:
    def __init__(self, filepath):
        self.filepath = filepath
        self.path=os.path.dirname(filepath)
        self.metadata = {}
        self.content = ''
        self.date = datetime.datetime.now()  # 添加默认日期
        self.categories = []  # 添加分类
        self.tags = []  # 添加标签
        self.slug = os.path.splitext(os.path.basename(filepath))[0]  # 添加slug
        self.type = os.path.splitext(filepath)[1][1:]  # 添加文件类型
        self.url = CONFIG['base_url']+'/'+self.path+'/'+self.slug+'.html'
        self.word_count = 0  # 添加字数统计
        self.parse()
    def parse(self):
            """根据文件类型调用相应的解析方法"""
            if self.type == 'md':
                self.parse_markdown()
            elif self.type == 'pdf':
                self.parse_pdf()
            elif self.type == 'html':
                self.parse_html()
            else:
                raise ValueError(f"Unsupported file type: {self.type}")

            # 统计字数
            self.category_count = len(self.categories)
            self.tag_count = len(self.tags)
            self.word_count = self._count_words()



    def _count_words(self):
        """统计文章字数"""
        if self.type == 'md':
            # 去除 Markdown 语法符号
            text = re.sub(r'[#*\-`~\[\]()>]', '', self.content)
        elif self.type == 'pdf':
            # PDF 内容已经是纯文本
            text = self.content
        elif self.type == 'html':
            # 去除 HTML 标签
            text = re.sub(r'<[^>]+>', '', self.content)
        else:
            text = self.content

        # 统计中文字数和英文单词数
        chinese_chars = len(re.findall(r'[\u4e00-\u9fa5]', text))
        english_words = len(re.findall(r'\b\w+\b', text))
        return chinese_chars + english_words

    def parse_markdown(self):
        with open(self.filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 分离元数据和内容
        if content.startswith('---'):
            parts = content.split('---', 2)
            if len(parts) >= 3:
                try:
                    self.metadata = yaml.safe_load(parts[1]) or {}
                    self.content = parts[2].strip()
                except yaml.YAMLError:
                    self.metadata = {}
                    self.content = content
        else:
            self.metadata = {}
            self.content = content.strip()


        # 处理元数据
        self.title = self.metadata.get('title', os.path.splitext(os.path.basename(self.filepath))[0])
        self.date = self._parse_date(self.metadata.get('date'))
        self.categories = self.metadata.get('categories', [])
        self.tags = self.metadata.get('tags', [])
        
        # 确保内容不为空
        if not self.content:
            self.content = "# " + self.title  # 如果内容为空，使用标题作为默认内容

        # 转换Markdown
        self.content = self._convert_markdown(self.content)

    def _parse_date(self, date_value):
        if isinstance(date_value, datetime.datetime):
            return date_value
        elif isinstance(date_value, datetime.date):
            return datetime.datetime.combine(date_value, datetime.time())
        elif isinstance(date_value, str):
            try:
                return datetime.datetime.strptime(date_value, '%Y-%m-%d')
            except ValueError:
                pass
        return datetime.datetime.now()

    def _generate_toc(self, html):
        """生成目录"""
        soup = BeautifulSoup(html, 'html.parser')
        
        # 查找所有标题
        headers = soup.find_all(['h2', 'h3', 'h4'])
        
        # 生成目录HTML
        toc_html = '<div class="toc-container">\n'
        toc_html += '<h3>目录</h3>\n<ul class="toc-list">\n'
        min_level = 10
        for header in headers:
            min_level = min(int(header.name[1]),min_level)
        for header in headers:

            # 为每个标题添加id
            if not header.get('id'):
                header['id'] = header.text.strip().replace(' ', '-').lower()
            
            # 根据标题级别设置缩进
            level = int(header.name[1]) - min_level
            toc_html += f'<li class="toc-item toc-level-{level}">'
            toc_html += f'<a href="#{header["id"]}">{header.text}</a></li>\n'
        
        toc_html += '</ul></div>'
        
        return toc_html, str(soup)

    def _convert_markdown(self, content):
        # 确保内容不为空
        if not content:
            return ""

        # 转换Markdown
        html = markdown.markdown(
            content,
            extensions=[
                'fenced_code',
                'codehilite',  # 添加代码高亮支持
                'tables',
                TocExtension(baselevel=2, toc_depth=3),
                'meta',
                'footnotes',
                'toc',
                'nl2br',
                'sane_lists',
                'admonition',
                'attr_list',
                'def_list',
                'abbr',
                'md_in_html',
                'pymdownx.arithmatex',
            ],
            extension_configs={
                'codehilite': {
                    'linenums': False,  # 显示行号
                    'css_class': 'highlight',  # 高亮样式类
                    'guess_lang': True,  # 自动检测语言
                    'use_pygments': True,  # 使用Pygments
                },
                'pymdownx.arithmatex': {
                    'generic': True,
                }
            },
            output_format='html5'
        )

        # 添加额外的样式类
        replacements = {
            '<table>': '<table class="markdown-table">',
            '<blockquote>': '<blockquote class="markdown-quote">',
            '<pre>': '<pre data-role="codeBlock" data-info="cpp" class="language-cpp cpp">',
            '<code>': '<code class="markdown-inline-code">'
        }

        for old, new in replacements.items():
            html = html.replace(old, new)

        # 生成目录
        toc_html, processed_html = self._generate_toc(html)
        
        # 获取目录
        self.toc = toc_html
        
        return processed_html

    def parse_pdf(self):
        """解析PDF文件"""
        try:
            # 读取PDF文件
            reader = PdfReader(self.filepath)
            
            # 提取元数据
            self.metadata = reader.metadata or {}
            
            # 设置标题
            self.title = self.metadata.get('/Title', os.path.splitext(os.path.basename(self.filepath))[0])

            # 从文件名解析分类和标签
            self._parse_filename()
            
            
            # 获取PDF修改时间
            self.date = self._get_pdf_modification_time()
            
            # 提取目录
            self.toc = self._extract_pdf_toc(reader)
            
            # 生成HTML内容
            self.content = self._generate_pdf_html()
            
        except Exception as e:
            print(f"Error parsing PDF: {e}")
            self.content = f"<p>Error loading PDF: {str(e)}</p>"

    def _parse_filename(self):
        """从文件名解析分类和标签"""
        filename = os.path.splitext(os.path.basename(self.filepath))[0]
        
        # 格式：分类1-分类2_标签1-标签2_文件名
        parts = filename.split('_')
        
        if len(parts) >= 3:
            # 解析分类
            if(parts[0]!=''):
                self.categories = parts[0].split('-')
            else:
                self.categories = []
            # 解析标签
            if(parts[1]!=''):
                self.tags = parts[1].split('-')
            else:
                self.tags = []
            # 设置标题
            self.title = ' '.join(parts[2:])
        elif len(parts) == 2:
            # 只有分类和标签
            self.categories = parts[0].split('-')
            self.tags = parts[1].split('-')
            self.title = self.metadata.get('/Title', 'Untitled')
        else:
            # 只有文件名
            self.categories = []
            self.tags = []
            self.title = self.metadata.get('/Title', filename)
        # print(self.title)

    def _extract_pdf_toc(self, reader):
        """生成PDF目录的HTML结构"""
        outlines = getattr(reader, 'outline', None)
        if not outlines:
            return '<div class="pdf-toc"><p>本PDF文件没有目录。</p></div>'
        
        # 生成目录 HTML
        toc_html = self._build_toc_html(reader, outlines)
        return f'<div class="pdf-toc toc-container">\n<h3>目录</h3>\n<ul class="toc-list">\n{toc_html}\n</div>'
    def _build_toc_html(self, reader, outline_items, level=0):
        """
        递归构建目录的HTML列表
        生成结构示例：
        <ul>
          <li><a href="#page1">章节1</a></li>
          <li>
            <a href="#page2">章节2</a>
            <ul>
              <li><a href="#page3">子章节2.1</a></li>
            </ul>
          </li>
        </ul>
        """
        html = ''
        for item in outline_items:
            if isinstance(item, list):
                # 嵌套目录递归生成
                html += self._build_toc_html(reader, item, level + 1)
            else:
                try:
                    title = item.title if hasattr(item, 'title') else str(item)
                    # 获取该目录项对应的页码（加1保证页码正常显示）
                    page_number = reader.get_destination_page_number(item) + 1
                    html += f'<li class="toc-item toc-level-{level}"><a href="#page{page_number}">{title}</a></li>\n'
                except Exception as e:
                    html += f'<li>Error: {str(e)}</li>\n'
        html += ''
        return html
    def _generate_pdf_html(self):
        """生成PDF展示的HTML"""
        pdf_url = f"{CONFIG['base_url']}/static/pdfs/{os.path.basename(self.filepath)}#toolbar=0&navpanes=0&sidebarViewOnLoad=0&scrollModeOnLoad=0&view=FitH"
        return f'{CONFIG['base_url']}/static/js/pdfjs/web/viewer.html?file={pdf_url}'

    def _get_pdf_modification_time(self):
        """获取PDF文件的修改时间"""
        try:
            # 获取文件修改时间
            mod_time = os.path.getmtime(self.filepath)
            # 转换为datetime对象
            return datetime.datetime.fromtimestamp(mod_time)
        except Exception as e:
            print(f"Error getting modification time: {e}")
            # 如果获取失败，返回当前时间
            return datetime.datetime.now()

    def parse_html(self):
        # HTML处理逻辑
        pass

    def save(self, output_dir):
        """保存文章到指定目录"""
        # 创建输出目录
        output_path = os.path.join(output_dir, os.path.dirname(self.filepath))
        os.makedirs(output_path, exist_ok=True)

        # 生成文件路径
        output_file = os.path.join(output_path, os.path.basename(self.filepath))

        # 写入文件
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(self.content)

class BlogGenerator:
    def __init__(self, config):
        self.config = config
        self.posts = []
        self.categories = {}
        self.tags = {}
        self.init_directories()
        self.load_posts()

    def init_directories(self):
        # 删除原有文件
        if os.path.exists(os.path.join(self.config['output_dir'], 'index.html')):
            os.remove(os.path.join(self.config['output_dir'], 'index.html'))
        if os.path.exists(os.path.join(self.config['output_dir'], 'base.html')):
            os.remove(os.path.join(self.config['output_dir'], 'base.html'))
        if os.path.exists(os.path.join(self.config['output_dir'], 'content')):
            shutil.rmtree(os.path.join(self.config['output_dir'], 'content'))
        if os.path.exists(os.path.join(self.config['output_dir'], 'static')):
            shutil.rmtree(os.path.join(self.config['output_dir'], 'static'))
        # 创建必要的目录
        os.makedirs(self.config['output_dir'], exist_ok=True)
        os.makedirs(os.path.join(self.config['output_dir'], 'content/posts'), exist_ok=True)
        os.makedirs(os.path.join(self.config['output_dir'], 'content/pages'), exist_ok=True)
        os.makedirs(os.path.join(self.config['output_dir'], 'content/index'), exist_ok=True)
        os.makedirs(os.path.join(self.config['output_dir'], 'static'), exist_ok=True)

    def load_posts(self):
        # 加载所有文章
        for root, dirs, files in os.walk(self.config['source_dir']):
            for file in files:
                if file.split('.')[-1] in self.config['extensions']:
                    post = Post(os.path.join(root, file))
                    self.posts.append(post)
        self.config['total_posts'] = len(self.posts)
        # 按日期排序
        self.posts.sort(key=lambda x: x.date, reverse=True)
        self._calculate_statistics()

    def _calculate_statistics(self):
        # 计算分类和标签统计
        for post in self.posts:
            # 统计分类
            for category in post.categories:
                self.categories[category] = [self.categories.get(category, [0,[]])[0] + 1,self.categories.get(category, [0,[]])[1]+[post]]
            # 统计标签
            for tag in post.tags:
                self.tags[tag] = [self.tags.get(tag, [0,[]])[0] + 1,self.tags.get(tag, [0,[]])[1]+[post]]
        # 按标签数量排序
        self.config['total_tags'] = len(self.tags)
        self.tags = sorted(self.tags.items(), key=lambda x: x[1][0], reverse=True)
        # 按分类数量排序
        self.config['total_categories'] = len(self.categories)
        self.categories = sorted(self.categories.items(), key=lambda x: x[1][0], reverse=True)
        # print(self.categories['算法竞赛'])


    def generate_site(self):
        # 生成整个站点
        self.copy_static_files()
        self.generate_base()
        self.generate_index()
        self.generate_posts()
        self.generate_categories()
        self.generate_tags()
        self.generate_guestbook()
        self.generate_rss()


    def copy_static_files(self):
        # 复制静态文件
        shutil.copytree(
            self.config['static_dir'],
            os.path.join(self.config['output_dir'], 'static'),
            dirs_exist_ok=True
        )
        pdf_output_dir = os.path.join(self.config['output_dir'], 'static/pdfs')
        os.makedirs(pdf_output_dir, exist_ok=True)
        for post in self.posts:
            if post.type == 'pdf':
                shutil.copy2(
                    post.filepath,
                    os.path.join(pdf_output_dir, os.path.basename(post.filepath))
                )

    def generate_base(self):
        # 生成基础模板
        template = env.get_template('base.html')
        context = {
            'site': self.config,
            'posts': self.posts[:5],  # 传递posts变量
            'categories': self.categories,
            'tags': self.tags,
            'now': datetime.datetime.now(),
            'type': 'base'
        }
        output = template.render(context)
        
        with open(os.path.join(self.config['output_dir'], 'base.html'), 'w', encoding='utf-8') as f:
            f.write(output)

    def generate_index(self, posts_per_page=CONFIG['per_page']):
        """生成首页，支持分页"""
        template = env.get_template("index.html")
        total_posts = len(self.posts)
        total_pages = (total_posts + posts_per_page - 1) // posts_per_page

        for page in range(1, total_pages + 1):
            start = (page - 1) * posts_per_page
            end = start + posts_per_page
            page_posts = self.posts[start:end]

            context = {
                'site': self.config,
                'posts': page_posts,
                'categories': self.categories,
                'tags': self.tags,
                'pagination': {
                    'current_page': page,
                    'total_pages': total_pages,
                    'has_prev': page > 1,
                    'prev_page': page - 1,
                    'has_next': page < total_pages,
                    'next_page': page + 1,
                    'page_list': range(1, total_pages + 1)
                },
                'now': datetime.datetime.now(),
                'type': 'index'
            }

            output = template.render(context)
            output_path = os.path.join(self.config['output_dir'],f'{"" if page == 1 else "content/index"}', f'index{"" if page == 1 else f"-{page}"}.html')
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(output)

    def generate_post(self, post):
        # 生成文章页面
        template = env.get_template('post.html')
        context = {
            'site': self.config,
            'post': post,
            'posts': self.posts[:5],  # 传递posts变量用于侧边栏
            'categories': self.categories,
            'tags': self.tags,
            'now': datetime.datetime.now(),
            'type': 'post'
        }
        output = template.render(context)
        
        output_path = os.path.join(self.config['output_dir'],os.path.dirname(post.filepath), f"{post.slug}.html")
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(output)
    def generate_posts(self):
        # 生成所有文章页面
        for post in self.posts:
            self.generate_post(post)
    def generate_categories(self):
        """生成分类页面"""
        # 创建分类目录
        categories_dir = os.path.join(self.config['output_dir'], 'content/categories')
        os.makedirs(categories_dir, exist_ok=True)

        # 生成所有分类页面
        self.generate_category_pages()

        # 生成分类索引页面
        self._generate_category_index()

    def generate_category_pages(self, posts_per_page=CONFIG['per_page']):
        """生成分类页面，支持分页"""
        template = env.get_template("category.html")
        for category, posts in self.categories:
            total_posts = posts[0]
            total_pages = (total_posts + posts_per_page - 1) // posts_per_page

            for page in range(1, total_pages + 1):
                start = (page - 1) * posts_per_page
                end = start + posts_per_page
                page_posts = posts[1][start:end]

                context = {
                    'site': self.config,
                    'category': category,
                    'posts': page_posts,
                    'post_count': len(posts[1]),
                    'pagination': {
                        'current_page': page,
                        'total_pages': total_pages,
                        'has_prev': page > 1,
                        'prev_page': page - 1,
                        'has_next': page < total_pages,
                        'next_page': page + 1,
                    },
                    'now': datetime.datetime.now(),
                    'tags': self.tags,
                }

                output = template.render(context)
                output_path = os.path.join(
                    self.config['output_dir'],
                    'content',
                    'categories',
                    f"{category.lower().replace(' ', '-')}{'' if page == 1 else f'-{page}'}.html"
                )
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(output)

    def _generate_category_index(self):
        """生成分类索引页面"""
        # 渲染模板
        template = env.get_template('categories.html')
        # print(self.categories)
        context = {
            'site': self.config,
            'categories': self.categories,
            'posts': self.posts,
            'now': datetime.datetime.now(),
            'type': 'categories',
            'tags': self.tags
        }
        # print(context['categories'])
        output = template.render(context)
        
        # 保存文件
        output_path = os.path.join(self.config['output_dir'], 'content/pages', 'categories.html')
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(output)

    def generate_tags(self):
        """生成标签页面，将输出目录调整到 /content/tags/ 下"""
        tags_dir = os.path.join(self.config['output_dir'], 'content', 'tags')
        os.makedirs(tags_dir, exist_ok=True)
        # 为每个标签生成单独页面
        self.generate_tag_pages()
        # 生成标签索引页面
        self._generate_tag_index()

    def generate_tag_pages(self, posts_per_page=CONFIG['per_page']):
        """生成标签页面，支持分页"""
        template = env.get_template("tag.html")
        for tag, posts in self.tags:
            total_posts = posts[0]
            total_pages = (total_posts + posts_per_page - 1) // posts_per_page

            for page in range(1, total_pages + 1):
                start = (page - 1) * posts_per_page
                end = start + posts_per_page
                page_posts = posts[1][start:end]

                context = {
                    'site': self.config,
                    'tag': tag,
                    'posts': page_posts,
                    'post_count': len(posts[1]),
                    'pagination': {
                        'current_page': page,
                        'total_pages': total_pages,
                        'has_prev': page > 1,
                        'prev_page': page - 1,
                        'has_next': page < total_pages,
                        'next_page': page + 1,
                    },
                    'now': datetime.datetime.now(),
                    'tags': self.tags
                }

                output = template.render(context)
                output_path = os.path.join(
                    self.config['output_dir'],
                    'content',
                    'tags',
                    f"{tag.lower().replace(' ', '-')}{'' if page == 1 else f'-{page}'}.html"
                )
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(output)

    def _generate_tag_index(self):
        """生成所有标签的索引页面"""
        template = env.get_template('tags.html')
        context = {
            'site': self.config,
            'tags': self.tags,
            'posts': self.posts,
            'now': datetime.datetime.now(),
            'type': 'tags'
        }
        output = template.render(context)
        output_path = os.path.join(self.config['output_dir'], 'content', 'pages', 'tags.html')
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(output)


    def generate_guestbook(self):
        # 生成留言板页面
        template = env.get_template('guestbook.html')
        context = {
            'site': self.config,
            'posts': self.posts,
            'now': datetime.datetime.now(),
            'type': 'guestbook'
        }
        output = template.render(context)
        output_path = os.path.join(self.config['output_dir'], 'content', 'pages', 'guestbook.html')
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(output)

    def generate_rss(self):
        # 生成RSS订阅
        pass

if __name__ == '__main__':
    CONFIG['base_url']=CONFIG['local_url']
    CONFIG['output_dir']='./local'
    generator = BlogGenerator(CONFIG)
    generator.generate_site()
    CONFIG['base_url']=CONFIG['public_url']
    CONFIG['output_dir']='./public'
    generator = BlogGenerator(CONFIG)
    generator.generate_site()