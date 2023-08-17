import sys
import requests
from PyQt5.QtWidgets import QApplication, QLabel, QLineEdit, QPushButton, QVBoxLayout, QWidget, QMessageBox, QHBoxLayout
from PyQt5.QtGui import QClipboard


def obter_dados_cnpj(cnpj):
    cnpj = ''.join(filter(str.isdigit, cnpj))
    url = f'https://www.receitaws.com.br/v1/cnpj/{cnpj}'
    response = requests.get(url)
    data = response.json()
    return data


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Consulta de CNPJ")
        self.layout = QVBoxLayout()

        self.label_cnpj = QLabel("Informe o CNPJ:")
        self.edit_cnpj = QLineEdit()
        self.button_consultar = QPushButton("Consultar")
        self.button_consultar.clicked.connect(self.consultar_cnpj)

        self.layout.addWidget(self.label_cnpj)
        self.layout.addWidget(self.edit_cnpj)
        self.layout.addWidget(self.button_consultar)

        self.info_labels = []
        self.copy_buttons = []
        self.info_layout = QVBoxLayout()

        self.scroll_area = QWidget()
        self.scroll_area.setLayout(self.info_layout)

        self.layout.addWidget(self.scroll_area)

        self.setLayout(self.layout)

    def consultar_cnpj(self):
        cnpj = self.edit_cnpj.text()

        if not cnpj:
            QMessageBox.warning(self, "Aviso", "Por favor, informe um CNPJ.")
            return

        cnpj = ''.join(filter(str.isdigit, cnpj))

        try:
            data = obter_dados_cnpj(cnpj)
            if 'error' in data:
                QMessageBox.warning(self, "Erro", f"Erro ao consultar CNPJ: {data['message']}")
            else:
                self.exibir_dados_empresa(data)
        except requests.exceptions.RequestException:
            QMessageBox.critical(self, "Limite Atingido", "O limite de consultas é de 3 CNPJs por minuto, aguarde um momento para tentar novamente.")

        self.edit_cnpj.clear()

    def exibir_dados_empresa(self, data):
        self.limpar_dados_empresa()

        fields = {
            'Nome': 'nome',
            'Nome fantasia': 'fantasia',
            'CNPJ': 'cnpj',
            'CEP': 'cep',
            'Endereço': 'logradouro',
            'Complemento': 'complemento',
            'Número': 'numero',
            'Bairro': 'bairro',
            'Cidade': 'municipio',
            'UF': 'uf',
            'Email': 'email',
            'Data de abertura': 'abertura',
            'Situação cadastral': 'situacao',
            'Telefone': 'telefone'
        }

        for label, field in fields.items():
            info_label = QLabel(f"{label}: {data.get(field, '')}")
            copy_button = QPushButton("Copiar")
            copy_button.clicked.connect(lambda _, text=data.get(field, ''): self.copiar_texto(text))

            info_layout = QHBoxLayout()
            info_layout.addWidget(info_label)
            info_layout.addWidget(copy_button)

            self.info_layout.addLayout(info_layout)

            self.info_labels.append(info_label)
            self.copy_buttons.append(copy_button)

    def limpar_dados_empresa(self):
        for label in self.info_labels:
            label.deleteLater()
        self.info_labels = []

        for button in self.copy_buttons:
            button.deleteLater()
        self.copy_buttons = []

    def copiar_texto(self, text):
        clipboard = QApplication.clipboard()
        clipboard.setText(text, mode=QClipboard.Clipboard)
        clipboard.setText(text, mode=QClipboard.Selection)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
