import tkinter as tk
from tkinter import filedialog, ttk
import pandas as pd
from itertools import product

class CSVComparatorApp:
    def __init__(self, master):
        self.master = master
        master.title("Comparador de CSV Interativo")
        master.geometry("1024x800")  # Define o tamanho da janela

        self.arquivo1 = None
        self.arquivo2 = None
        self.data1 = None
        self.data2 = None

        # Frame para organizar os previews
        self.frame_previews = tk.Frame(master)
        self.frame_previews.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Frame para a Treeview de linhas repetidas
        self.frame_repetidas = tk.Frame(master)
        self.frame_repetidas.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

        # Define a altura dos previews (metade da altura da janela)
        preview_height = 350 #800/2

        # Áreas de texto para visualização dos dados (limitado a 3 colunas)
        self.tree1 = ttk.Treeview(self.frame_previews, show="headings", height=int(preview_height/20))#numero de linhas visiveis
        self.tree1.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.tree2 = ttk.Treeview(self.frame_previews, show="headings", height=int(preview_height/20))
        self.tree2.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Área de texto para visualização das linhas repetidas
        self.tree_repetidas = ttk.Treeview(self.frame_repetidas, show="headings", height=int(preview_height/20))
        self.tree_repetidas.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

        # Barra de rolagem para as tabelas (com o mesmo tamanho)
        self.scrollbar1 = ttk.Scrollbar(self.frame_previews, orient="vertical", command=self.tree1.yview)
        self.scrollbar1.pack(side=tk.LEFT, fill="y")
        self.tree1.configure(yscrollcommand=self.scrollbar1.set)

        self.scrollbar2 = ttk.Scrollbar(self.frame_previews, orient="vertical", command=self.tree2.yview)
        self.scrollbar2.pack(side=tk.RIGHT, fill="y")
        self.tree2.configure(yscrollcommand=self.scrollbar2.set)

        self.scrollbar_repetidas = ttk.Scrollbar(self.frame_repetidas, orient="vertical", command=self.tree_repetidas.yview)
        self.scrollbar_repetidas.pack(side=tk.LEFT, fill="y")
        self.tree_repetidas.configure(yscrollcommand=self.scrollbar_repetidas.set)

        # Botões para selecionar os arquivos (mantidos abaixo das Treeviews)
        self.btn_selecionar1 = tk.Button(master, text="Selecionar Arquivo 1", command=self.selecionar_arquivo1)
        self.btn_selecionar1.pack(side = tk.TOP, pady=5)

        self.btn_selecionar2 = tk.Button(master, text="Selecionar Arquivo 2", command=self.selecionar_arquivo2)
        self.btn_selecionar2.pack(side = tk.TOP, pady=5)


        # Label para exibir informações adicionais
        self.info_label = tk.Label(master, text="")
        self.info_label.pack(pady=10)

    def selecionar_arquivo1(self):
        self.arquivo1 = filedialog.askopenfilename(filetypes=[("Arquivos CSV", "*.csv")])
        if self.arquivo1:
            self.data1 = self.carregar_csv(self.arquivo1)
            self.exibir_dados(self.tree1, self.data1, num_colunas=3) # Exibe apenas as 3 primeiras colunas
            self.comparar_arquivos()

    def selecionar_arquivo2(self):
        self.arquivo2 = filedialog.askopenfilename(filetypes=[("Arquivos CSV", "*.csv")])
        if self.arquivo2:
            self.data2 = self.carregar_csv(self.arquivo2)
            self.exibir_dados(self.tree2, self.data2, num_colunas=3) # Exibe apenas as 3 primeiras colunas
            self.comparar_arquivos()

    def carregar_csv(self, arquivo):
        try:
            df = pd.read_csv(arquivo)
            return df
        except Exception as e:
            print(f"Erro ao carregar o arquivo CSV: {e}")
            return None

    def exibir_dados(self, tree, data, num_colunas=None):
        """Exibe os dados na Treeview, limitado ao número de colunas especificado."""
        # Limpa a Treeview
        for item in tree.get_children():
            tree.delete(item)

        if data is None:
            return

        colunas = list(data.columns[:num_colunas]) if num_colunas else list(data.columns)

        # Define as colunas
        tree["columns"] = colunas
        for col in colunas:
            tree.heading(col, text=col)
            tree.column(col, width=100)  # Ajuste a largura conforme necessário

        # Insere os dados
        for index, row in data.iterrows():
            tree.insert("", "end", values=list(row[:num_colunas]) if num_colunas else list(row))

    def exibir_linhas_repetidas(self, tree, repeticoes):
        """Exibe as linhas repetidas na Treeview separada."""
        # Limpa a Treeview
        for item in tree.get_children():
            tree.delete(item)

        # Define as colunas
        tree["columns"] = ("Valor", "Arquivo", "Linha")
        tree.heading("Valor", text="Valor")
        tree.heading("Arquivo", text="Arquivo")
        tree.heading("Linha", text="Linha")
        tree.column("Valor", width=200)  # Ajuste a largura conforme necessário
        tree.column("Arquivo", width=100)
        tree.column("Linha", width=100)


        # Insere os dados
        for valor, localizacoes in repeticoes.items():
            for arquivo, linha in localizacoes:
                tree.insert("", "end", values=(valor, arquivo, linha))


    def comparar_arquivos(self):
        if self.data1 is None or self.data2 is None:
            self.info_label.config(text="Selecione os dois arquivos CSV para comparar.")
            return

        # Limpa as tags de igualdade anteriores
        self.tree1.tag_configure("igual", background="")
        self.tree2.tag_configure("igual", background="")

        repeticoes = {}  # Dicionário para armazenar informações repetidas
        colunas_iguais = 0
        artigos_duplicados = 0 # Contador de artigos duplicados

        # Converter DataFrames para listas de tuplas (primeiras duas colunas)
        lista_data1 = [tuple(row[:2].astype(str).str.strip()) for _, row in self.data1.iterrows()]
        lista_data2 = [tuple(row[:2].astype(str).str.strip()) for _, row in self.data2.iterrows()]

        # Comparar todas as combinações de linhas entre os dois arquivos
        linhas_duplicadas = set() #set para guardar as linhas duplicadas e nao contar varias vezes a mesma linha
        for (i1, linha1), (i2, linha2) in product(enumerate(lista_data1), enumerate(lista_data2)): #product para comparar todos com todos
            if linha1 == linha2:
                # Destacar linhas iguais
                self.destacar_linha(self.tree1, i1, "lightblue")
                self.destacar_linha(self.tree2, i2, "lightblue")
                
                #Registrar a repetição da linha e suas posições
                valor_linha = tuple(linha1) #converte a linha em tupla para usar como chave
                if valor_linha not in repeticoes:
                    repeticoes[valor_linha] = []

                # Adiciona as linhas duplicadas ao set e conta
                if (1, i1) not in linhas_duplicadas:
                    repeticoes[valor_linha].append((1, i1))
                    linhas_duplicadas.add((1, i1))
                if (2, i2) not in linhas_duplicadas:
                    repeticoes[valor_linha].append((2, i2))
                    linhas_duplicadas.add((2, i2))


        # Contar artigos duplicados (contando apenas uma vez para cada valor duplicado)
        artigos_duplicados = len(set(repeticoes.keys()))


        # Comparar colunas (esta parte permanece a mesma)
        for col in self.data1.columns:
            if col in self.data2.columns and self.data1[col].astype(str).str.strip().equals(self.data2[col].astype(str).str.strip()):
                colunas_iguais += 1
                self.info_label.config(text=self.info_label.cget("text") + f"\nColuna '{col}' é igual.")

        # Exibir informações sobre repetições na Treeview separada
        self.exibir_linhas_repetidas(self.tree_repetidas, repeticoes)

        self.info_label.config(text=f"Artigos Duplicados: {artigos_duplicados}\nColunas iguais: {colunas_iguais}")

    def destacar_linha(self, tree, row_index, color):
        """Destaca uma linha específica na Treeview."""
        try:
            item_id = tree.get_children()[row_index]
            tree.tag_configure("destaque", background=color)
            tree.item(item_id, tags=("destaque",))
        except IndexError:
            print(f"Índice de linha {row_index} fora dos limites da Treeview.")
        except Exception as e:
            print(f"Erro ao destacar linha: {e}")

    def destacar_celula(self, tree, row_index, column_name, color):
        """
        Destaca uma célula específica na Treeview.

        Args:
            tree (ttk.Treeview): A Treeview na qual destacar a célula.
            row_index (int): O índice da linha da célula.
            column_name (str): O nome da coluna da célula.
            color (str): A cor de fundo para destacar a célula.
        """
        try:
            item_id = tree.get_children()[row_index]
            tree.set(item_id, column=column_name, value=tree.set(item_id, column=column_name))  # Força atualização
            tree.tag_configure("destaque", background=color)
            tree.item(item_id, tags=("destaque",))
        except IndexError:
            print(f"Índice de linha {row_index} fora dos limites da Treeview.")
        except Exception as e:
            print(f"Erro ao destacar célula: {e}")

root = tk.Tk()
app = CSVComparatorApp(root)
root.mainloop()