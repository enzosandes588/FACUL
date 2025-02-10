import tkinter as tk
from tkinter import filedialog, ttk
import pandas as pd
from itertools import product

class CSVComparatorApp:
    def __init__(self, master):
        self.master = master
        master.title("Comparador de CSV Interativo")
        master.geometry("1024x800")  

        self.arquivo1 = None
        self.arquivo2 = None
        self.data1 = None
        self.data2 = None

      
        self.frame_previews = tk.Frame(master)
        self.frame_previews.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

       
        self.frame_repetidas = tk.Frame(master)
        self.frame_repetidas.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

   
        preview_height = 350 

      
        self.tree1 = ttk.Treeview(self.frame_previews, show="headings", height=int(preview_height/20))
        self.tree1.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.tree2 = ttk.Treeview(self.frame_previews, show="headings", height=int(preview_height/20))
        self.tree2.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

       
        self.tree_repetidas = ttk.Treeview(self.frame_repetidas, show="headings", height=int(preview_height/20))
        self.tree_repetidas.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

     
        self.scrollbar1 = ttk.Scrollbar(self.frame_previews, orient="vertical", command=self.tree1.yview)
        self.scrollbar1.pack(side=tk.LEFT, fill="y")
        self.tree1.configure(yscrollcommand=self.scrollbar1.set)

        self.scrollbar2 = ttk.Scrollbar(self.frame_previews, orient="vertical", command=self.tree2.yview)
        self.scrollbar2.pack(side=tk.RIGHT, fill="y")
        self.tree2.configure(yscrollcommand=self.scrollbar2.set)

        self.scrollbar_repetidas = ttk.Scrollbar(self.frame_repetidas, orient="vertical", command=self.tree_repetidas.yview)
        self.scrollbar_repetidas.pack(side=tk.LEFT, fill="y")
        self.tree_repetidas.configure(yscrollcommand=self.scrollbar_repetidas.set)

     
        self.btn_selecionar1 = tk.Button(master, text="Selecionar Arquivo 1", command=self.selecionar_arquivo1)
        self.btn_selecionar1.pack(side = tk.TOP, pady=5)

        self.btn_selecionar2 = tk.Button(master, text="Selecionar Arquivo 2", command=self.selecionar_arquivo2)
        self.btn_selecionar2.pack(side = tk.TOP, pady=5)


    
        self.info_label = tk.Label(master, text="")
        self.info_label.pack(pady=10)

    def selecionar_arquivo1(self):
        self.arquivo1 = filedialog.askopenfilename(filetypes=[("Arquivos CSV", "*.csv")])
        if self.arquivo1:
            self.data1 = self.carregar_csv(self.arquivo1)
            self.exibir_dados(self.tree1, self.data1, num_colunas=3) 
            self.comparar_arquivos()

    def selecionar_arquivo2(self):
        self.arquivo2 = filedialog.askopenfilename(filetypes=[("Arquivos CSV", "*.csv")])
        if self.arquivo2:
            self.data2 = self.carregar_csv(self.arquivo2)
            self.exibir_dados(self.tree2, self.data2, num_colunas=3) 
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
 
        for item in tree.get_children():
            tree.delete(item)

        if data is None:
            return

        colunas = list(data.columns[:num_colunas]) if num_colunas else list(data.columns)

     
        tree["columns"] = colunas
        for col in colunas:
            tree.heading(col, text=col)
            tree.column(col, width=100)  

  
        for index, row in data.iterrows():
            tree.insert("", "end", values=list(row[:num_colunas]) if num_colunas else list(row))

    def exibir_linhas_repetidas(self, tree, repeticoes):
        """Exibe as linhas repetidas na Treeview separada."""

        for item in tree.get_children():
            tree.delete(item)

   
        tree["columns"] = ("Valor", "Arquivo", "Linha")
        tree.heading("Valor", text="Valor")
        tree.heading("Arquivo", text="Arquivo")
        tree.heading("Linha", text="Linha")
        tree.column("Valor", width=200)  
        tree.column("Arquivo", width=100)
        tree.column("Linha", width=100)



        for valor, localizacoes in repeticoes.items():
            for arquivo, linha in localizacoes:
                tree.insert("", "end", values=(valor, arquivo, linha))


    def comparar_arquivos(self):
        if self.data1 is None or self.data2 is None:
            self.info_label.config(text="Selecione os dois arquivos CSV para comparar.")
            return

     
        self.tree1.tag_configure("igual", background="")
        self.tree2.tag_configure("igual", background="")

        repeticoes = {}  
        colunas_iguais = 0
        artigos_duplicados = 0 

  
        lista_data1 = [tuple(row[:2].astype(str).str.strip()) for _, row in self.data1.iterrows()]
        lista_data2 = [tuple(row[:2].astype(str).str.strip()) for _, row in self.data2.iterrows()]

      
        linhas_duplicadas = set() 
        for (i1, linha1), (i2, linha2) in product(enumerate(lista_data1), enumerate(lista_data2)): 
            if linha1 == linha2:
              
                self.destacar_linha(self.tree1, i1, "lightblue")
                self.destacar_linha(self.tree2, i2, "lightblue")
                
                
                valor_linha = tuple(linha1) 
                if valor_linha not in repeticoes:
                    repeticoes[valor_linha] = []

               
                if (1, i1) not in linhas_duplicadas:
                    repeticoes[valor_linha].append((1, i1))
                    linhas_duplicadas.add((1, i1))
                if (2, i2) not in linhas_duplicadas:
                    repeticoes[valor_linha].append((2, i2))
                    linhas_duplicadas.add((2, i2))


       
        artigos_duplicados = len(set(repeticoes.keys()))


      
        for col in self.data1.columns:
            if col in self.data2.columns and self.data1[col].astype(str).str.strip().equals(self.data2[col].astype(str).str.strip()):
                colunas_iguais += 1
                self.info_label.config(text=self.info_label.cget("text") + f"\nColuna '{col}' é igual.")

       
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
            tree.set(item_id, column=column_name, value=tree.set(item_id, column=column_name))  
            tree.tag_configure("destaque", background=color)
            tree.item(item_id, tags=("destaque",))
        except IndexError:
            print(f"Índice de linha {row_index} fora dos limites da Treeview.")
        except Exception as e:
            print(f"Erro ao destacar célula: {e}")

root = tk.Tk()
app = CSVComparatorApp(root)
root.mainloop()
