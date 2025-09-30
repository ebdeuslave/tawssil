import re, sys, os
from datetime import date
import winsound as ws
from tkinter import (Tk, ttk, Menu, messagebox as msg, Button, Checkbutton, Toplevel, Label, LabelFrame, StringVar, IntVar, OptionMenu, Entry, HORIZONTAL, filedialog)
from threading import Thread
from pathlib import Path
from utils import *
from configuration import *
from Http.ParaAPI import ParaApi
from Http.TawssilAPI import TawssilAPI
from Http.PrestashopAPI import PrestashopAPI
from Http.GmailAPI import GmailAPI
from Core.HandleJsonFiles import HandleJsonFiles
from Core.HandlePdfFiles import HandlePdfFiles
from Core.Formatter import Formatter
from Core.Checker import Checker
from Core.Payment import Payment
from Core.Settings import Settings
import webbrowser
from pushToGithub import autoPush


class TawssilApp(Tk):
    def __init__(self):
        super().__init__()
        self.theme_color = "mediumpurple3"
        self.icon = "Images/tawssil.ico"
        self.title("Tawssil Delivery v1")
        self.geometry("1000x900+700+30")
        self.configure(background=self.theme_color)
      
        if os.path.isfile(self.icon): self.iconbitmap(self.icon)

        self.json_files = {
            "history": "history/shipmentsHistory",
            "orders": "history/addedOrders",
            "shipmentsNumbers": "history/readyToPrint"
        }
        
          
    ############################## Frontend Methods ##############################

    # UI
    def Widgets(self):
        # Menu
        menu = Menu()
        self.tools_menu = Menu(menu, tearoff=False)
        menu.add_cascade(label='Tools', menu=self.tools_menu)
        self.tools_menu.add_command(label='Update orders status', command=lambda: Thread(target=self.updateOrdersStatus).start())   
        self.tools_menu.add_command(label='Update Package', command=self.updatePackageUI)  
        self.tools_menu.add_command(label='Return of funds', command=self.paymentUI)
        self.tools_menu.add_command(label='Shortcuts', command=self.shortcutsUI)        
        
        self.settings_menu = Menu(menu, tearoff=False)
        menu.add_cascade(label='Settings', menu=self.settings_menu)
        self.settings_menu.add_command(label="Configure", command=self.settingsUI)
        self.settings_menu.add_command(label='Reset UI', command=self.resetWindow)
        
        self.config(menu=menu)
        
        # Create Package
        self.packageCreationFrame = LabelFrame(self, border=8,text='Create Package', font=("Helvetica", "15", 'bold'), bg=self.theme_color)
        self.packageCreationFrame.pack(pady=20)

        self.stores = ['Parapharma', 'Coinpara', 'Parabio', 'Allopara', 'Laparfumerie', 'Benecos', 'Chezpara', 'Couchebio', 'Ecolunes', 'Pingo','Africa internet holding', 'Autre']
        self.store_selected = StringVar()
        self.store_selected.set(self.stores[0])
        drop = OptionMenu( self.packageCreationFrame , self.store_selected , *self.stores )
        drop.pack(pady=5)
        drop["menu"].configure(bg="lightgreen", borderwidth=1, font=("Helvetica", "9", 'bold'))

        Label(self.packageCreationFrame,text='Delivery type', bg=self.theme_color).pack()
        self.types = ['Normal', 'Return']
        self.type_selected = StringVar()
        self.type_selected.set(self.types[0])
        drop = OptionMenu( self.packageCreationFrame , self.type_selected , *self.types )
        drop.pack(pady=5)
        drop["menu"].configure(bg="lightgreen", borderwidth=1, font=("Helvetica", "9", 'bold'))

        Label(self.packageCreationFrame,text='ID/Name', bg=self.theme_color).pack()
        self.ID = Entry(self.packageCreationFrame, width=10)
        self.ID.pack()
        self.ID.focus()

        Label(self.packageCreationFrame,text='Amount', bg=self.theme_color).pack()
        self.price = Entry(self.packageCreationFrame, width=5)
        self.price.pack()

        Label(self.packageCreationFrame,text='City', bg=self.theme_color).pack()
        self.city = Entry(self.packageCreationFrame, width=15)
        self.city.pack() 

        Label(self.packageCreationFrame,text='Address', bg=self.theme_color).pack()
        self.deliveryAddress = Entry(self.packageCreationFrame, width=15)
        self.deliveryAddress.pack() 

        Label(self.packageCreationFrame,text='Phone', bg=self.theme_color).pack()
        self.contactPhone = Entry(self.packageCreationFrame, width=15)
        self.contactPhone.pack()

        Label(self.packageCreationFrame,text='Remark', bg=self.theme_color).pack()
        self.remark = Entry(self.packageCreationFrame, width=50)
        self.remark.pack() 

        self.urgent_var = IntVar()
        self.urgent = Checkbutton(self.packageCreationFrame, text="Urgent", variable=self.urgent_var, onvalue=1, offvalue=0, bg=self.theme_color, command=self.addUrgentMsg)
        self.urgent.pack() 

        self.tasks = ['Auto', 'Manual', 'Refund']
        self.task = StringVar()
        self.task.set(self.tasks[0])
        self.tasks_drop = OptionMenu( self.packageCreationFrame , self.task , *self.tasks )
        self.tasks_drop.pack(pady=5)
        self.tasks_drop["menu"].configure(bg="lightgreen", borderwidth=1, font=("Helvetica", "9", 'bold'))

        self.do = Button(self.packageCreationFrame, text="Go",command= lambda: Thread(target=self.post).start(),activebackground='white',activeforeground='white',bg='lightgreen',bd =5,padx=5,pady=3,width=12,font='mincho 9')
        self.do.pack(pady=10)

        self.bind('<Return>', lambda x: Thread(target=self.post).start())
        self.bind('<Prior>', lambda x: Thread(target=self.post).start())
        self.bind('<Control-p>', lambda x: Thread(target=self.printLabels, args=("auto",)).start())
        self.bind('<Control-s>', lambda x: Thread(target=self.updateOrdersStatus).start())
        self.bind('<Control-r>', lambda x: Thread(target=self.resetWindow).start())
        self.bind('<Control-u>', lambda x: Thread(target=self.urgentShortcut).start())
        # change store shortcuts
        self.bind('<Control-Alt-p>', lambda store: self.changeStore("Parapharma"))
        self.bind('<Alt-c>', lambda store: self.changeStore("Coinpara"))
        self.bind('<Alt-p>', lambda store: self.changeStore("Parabio"))
        self.bind('<Alt-a>', lambda store: self.changeStore("Allopara"))
        self.bind('<Alt-l>', lambda store: self.changeStore("Laparfumerie"))
        self.bind('<Alt-b>', lambda store: self.changeStore("Benecos"))
        

        # Hold <Total Packages> and <Print Labels> frames side-by-side in one frame
        self.package_info_frame = LabelFrame(self.packageCreationFrame, bg=self.theme_color)
        self.package_info_frame.pack(pady=20)
        
        # Total Packages
        self.totalPackagesFrame = LabelFrame(self.package_info_frame, border=8, text='Total Packages', font=("Helvetica", "15", 'bold'), bg=self.theme_color)
        self.totalPackagesFrame.pack(side="left", padx=20, anchor='n')
        
        self.totalIDs = Label(self.totalPackagesFrame, text=f"Total: {len(HandleJsonFiles.read(self.json_files['orders']))}", width=20, font=("Helvetica", "10", 'bold'), bg=self.theme_color)
        self.totalIDs.pack(pady=1)

        self.totalCmdReady = Label(self.totalPackagesFrame, text=f"Ready to print: {len(HandleJsonFiles.read(self.json_files['shipmentsNumbers']))}", width=20, font=("Helvetica", "10", 'bold'), bg=self.theme_color)
        self.totalCmdReady.pack(pady=1)

        self.stateLabel = Label(self.totalPackagesFrame, width=50, bd=2, font=("Helvetica", "13", 'bold'), bg=self.theme_color)
        self.stateLabel.pack(pady=5)
        self.progress = ttk.Progressbar(self.totalPackagesFrame, orient=HORIZONTAL, length=300, mode='determinate')

        # Print Labels
        self.labelsFrame = LabelFrame(self.package_info_frame, border=8, text='Print Labels', font=("Helvetica", "15", 'bold'), bg=self.theme_color)
        self.labelsFrame.pack(side="right", padx=20, anchor='n')  

        self.generateLabelAuto = Button(self.labelsFrame, bg=self.theme_color, text="Auto", command=lambda: Thread(target=self.printLabels, args=("auto",)).start())
        self.generateLabelAuto.pack(pady=5)

        Label(self.labelsFrame, text='IDs (Separate by ",")', bg=self.theme_color).pack()
        self.shipments_numbers = Entry(self.labelsFrame, width=50)
        self.shipments_numbers.pack(pady=10)

        self.generateLabelManual = Button(self.labelsFrame, bg=self.theme_color, text="Manual", command=lambda: Thread(target=self.printLabels, args=("manual",)).start())
        self.generateLabelManual.pack(pady=5)

        self.download_label = Label(self.labelsFrame, text='', bg=self.theme_color)
        self.download_label.pack()
    
    
    def shortcutsUI(self):
        msg.showinfo("Shortcuts", """
                     Reset UI : CTRL+r
                     Auto Print : CTRL+p
                     Update Status : CTRL+s
                     Add Urgent: CTRL+u
                     Change store:
                                Parapharma: CTRL+Alt+p or Reset UI
                                Coinpara:Alt+c
                                Parabio:Alt+p
                                Allopara:Alt+a
                                Laparafumerie:Alt+l
                                Benecos:Alt+b
                     """)
        
        
    def paymentUI(self):
        self.tools_menu.entryconfig(2, state="disabled")
        self.rdf_window = Toplevel(self)
        self.rdf_window.title("Return of funds")
        self.rdf_window.configure(background=self.theme_color)
        self.rdf_window.geometry("500x500")
        if os.path.isfile(self.icon): self.rdf_window.iconbitmap(self.icon)

        self.autoFrame = LabelFrame(self.rdf_window, border=8,text='Auto', font=("Helvetica", "15", 'bold'), bg=self.theme_color)
        self.autoFrame.pack(pady=20)
        self.autoSetPaymentBtn = Button(self.autoFrame, text="Set", command=lambda: Thread(target=self.autoSetPayment).start(), activebackground='white',activeforeground='black',bg='lightgreen',bd =1,padx=1,pady=1,width=10,font='calibri 10')
        self.autoSetPaymentBtn.pack(pady=20)

        self.manualFrame = LabelFrame(self.rdf_window, border=8,text='Manual', font=("Helvetica", "15", 'bold'), bg=self.theme_color)
        self.manualFrame.pack()

        browse = Button(self.manualFrame, text='Select file (.xlsx Only)', command=self.getFileDirectory,width=18)
        browse.pack(pady=20)
        self.filePathLabel = Label(self.manualFrame, text='/PATH/')
        self.filePathLabel.pack(padx=1,pady=1)
        self.manualSetPaymentBtn = Button(self.manualFrame, state="disabled", text="Select file first", command=lambda: Thread(target=self.manualSetPayment).start(), activebackground='white',activeforeground='black',bg='lightgreen',bd =1,padx=1,pady=1,width=25,font='calibri 10')
        self.manualSetPaymentBtn.pack(pady=20)
        self.payment_info = Label(self.manualFrame,text="", bd=7,bg='gold', width=40)
        self.payment_info.pack(pady=20)
        
        self.rdf_window.protocol("WM_DELETE_WINDOW", self.onPaymentWindowClosed) 
        

    def updatePackageUI(self):
        self.update_package_window = Toplevel(self)
        self.update_package_window.title("Update Package")
        self.update_package_window.configure(background=self.theme_color)
        self.update_package_window.geometry("500x500")
        if os.path.isfile(self.icon): self.update_package_window.iconbitmap(self.icon)
        
        Label(self.update_package_window,text='Package number', bg=self.theme_color).pack()
        self.packageNumber = Entry(self.update_package_window, width=30)
        self.packageNumber.pack(pady=20)
        
        Label(self.update_package_window,text='New Phone', bg=self.theme_color).pack()
        self.newPhone = Entry(self.update_package_window, width=30)
        self.newPhone.pack(pady=20)


        Label(self.update_package_window,text='New Amount', bg=self.theme_color).pack()
        self.newAmount = Entry(self.update_package_window, width=5)
        self.newAmount.pack(pady=20)
        
        self.updatePackageBtn = Button(self.update_package_window, text="Update", command=lambda: Thread(target=self.updatePackage).start(), activebackground='white',activeforeground='black',bg='lightgreen',bd =1,padx=1,pady=1,width=10,font='calibri 10')
        self.updatePackageBtn.pack(pady=20)
        
        
    def settingsUI(self):
        self.settings_window = Toplevel(self)
        self.settings_window.title("Settings")
        self.settings_window.configure(background=self.theme_color)
        self.settings_window.geometry("300x300")
        self.settings_window.resizable(False, False)
        if os.path.isfile(self.icon): self.settings_window.iconbitmap(self.icon)
        
        Label(self.settings_window,text='Printer', bg=self.theme_color).pack()
        self.printers = ["HP","Deli"]
        self.printerSelected = StringVar()
        self.printerSelected.set(Settings.getPrinter())
        self.printers_drop = OptionMenu(self.settings_window, self.printerSelected, *self.printers)
        self.printers_drop.pack(pady=5)
        self.printers_drop["menu"].configure(bg=self.theme_color, borderwidth=1, font=("Helvetica", "9", 'bold')) 
        
        Label(self.settings_window,text='Auto Print', bg=self.theme_color).pack()
        self.autoPrintValue = IntVar()
        self.autoPrintBtn = Checkbutton(self.settings_window, text="Active", bg=self.theme_color, variable=self.autoPrintValue, onvalue=1, offvalue=0, command=self.onActiveAutoPrint)
        self.autoPrintBtn.pack()
        self.autoPrintValue.set(Settings.autoPrint())
        Label(self.settings_window,text='Total shipments to start printing', bg=self.theme_color).pack()
        self.total_to_print = Entry(self.settings_window, width=3)
        self.total_to_print.insert(0, Settings.totalToPrintAuto())
        self.total_to_print.pack(pady=2)
        if not Settings.autoPrint():
            self.total_to_print.config(state="disabled")
        
        self.save_settings_btn = Button(self.settings_window,bg=self.theme_color, text="Save",command=self.saveSettings)
        self.save_settings_btn.pack(pady=5)

    # Actions
    def getManualFields(self):
        return {
            "name": self.ID.get(),
            "city" : self.city.get().strip(),
            "address" : self.deliveryAddress.get(),
            "total" : int( re.sub( "[^0-9]", "", self.price.get() ) ) if self.price.get() else "",
            "phone" : re.sub("[^0-9]", "", self.contactPhone.get()),
            "remark" : self.remark.get() if self.remark.get() else "ATTENTION : Produits Fragiles"
        }
        

    def enableDisableWidgets(self, frames:list):
        for frame in frames:
            try:
                for child in frame.winfo_children():
                    if child["state"] == "normal":
                        child.configure(state='disabled')
                    else:
                        child.configure(state='normal')
            except Exception as e:
                continue


    def resetEntries(self, frame):
        for child in frame.winfo_children():
            try: child.delete(0, 'end')
            except: pass
        self.type_selected.set(self.types[0])
        self.urgent_var.set(0)
        self.ID.focus()


    def resetWindow(self):
        for widget in self.packageCreationFrame.winfo_children():
            try: 
                widget.configure(state='normal')
                widget.delete(0, 'end')
            except: pass

        self.store_selected.set(self.stores[0])
        self.task.set(self.tasks[0])
        self.type_selected.set(self.types[0])
        self.urgent_var.set(0)
        self.ID.focus()


    def changeStore(self, store):
        self.store_selected.set(store)
        
        
    def onPaymentWindowClosed(self):
        """
        Reactive menu after closing window to prevent opening more than 1
        """
        self.tools_menu.entryconfig(2, state="normal")
        self.rdf_window.destroy()
    
    
    def getFileDirectory(self):
        self.filePath = filedialog.askopenfilename()
        if self.filePath.endswith('xlsx'):      
            self.filePathLabel.configure(text=self.filePath) 
            self.manualSetPaymentBtn.config(state="active", text='Set')
        else:
            self.filePathLabel.configure(text='/PATH/')
            self.manualSetPaymentBtn.config(state="disabled", text="Select file first")


    def addUrgentMsg(self):
        if self.urgent_var.get():
            self.remark.insert(0, "URGENT SVP")
        else:
            self.remark.delete(0, "end")


    def urgentShortcut(self):
        if not self.remark.get():
            self.urgent.select()
            self.remark.insert(0, "URGENT SVP")
        else:
            self.urgent.deselect()
            self.remark.delete(0, "end")
        
        
    def onActiveAutoPrint(self):
        if self.autoPrintValue.get():
            self.total_to_print.config(state="normal")
        else:
            self.total_to_print.config(state="disabled")

    ############################## Backend Methods ##############################
    def post(self, event=None):
        task = self.task.get()

        if task == "Auto":
            self.autoCreateShipment()
        elif task == "Manual":
            self.manualCreateShipment()
        elif task == "Refund":
            self.refund()
        else:
            msg.showwarning("Task not accessible", f"Task {task} Not Found")

        self.task.set(self.tasks[0])


    def saveSettings(self):
        if not self.autoPrintValue.get():
            self.total_to_print.config(state="disabled")
        elif not self.total_to_print.get().isdigit():
            return msg.showerror("Settings", "Total shipments to start printing must be a number")
        
        new_settings = {
                "autoPrint": {
                    "active": self.autoPrintValue.get(),
                    "total_to_print": self.total_to_print.get(),
                    }, 
                "printer": self.printerSelected.get(),
            }
                    
        Settings.apply(new_settings)
        
        if self.printerSelected.get() == "HP":
            msg.showwarning("IMPORTANT before printing using HP", 'To use HP printer you should change pages per sheet option to 4 to print label in 10x10 (4 labels in one page)\n\nTap Windows Key\nType "Printers"\nClick on "Printers & scanners"\nClick on HP then Manage\nClick on Printing preferences\nChange Pages per sheet to 4')

        return msg.showinfo("Settings", "Settings changed successfully")
        
        
    def autoSetPayment(self):
        self.autoSetPaymentBtn.config(state="disabled")
        try:
            emptyDirectory("attachements")

            data = {
                "sender": "wijdane.fares@tawssil.ma",
                "subject": "état de paiement global.",
                # "filename": "Parapharmacie-AIH état de paiement MBS global du Mois Septembre.xlsx",
                "maxResult": 20
            }

            gmailAPI = GmailAPI(GMAIL_TOKEN_FILE, GMAIL_CREDENTIALS_FILE)
            
            downloadAttachementResponse = gmailAPI.downloadAttachement(data, GMAIL_DOWNLOAD_FOLDER)
            
            if downloadAttachementResponse["hasError"]:
                msg.showwarning("GmailAPI", downloadAttachementResponse["content"])
            else:
                # downloadAttachement method changed dir to attachements therefor the cwd is attachement/
                files = os.listdir(os.getcwd())
                files.reverse()
                
                for file in files:
                    payment = Payment()
                    set_payment = payment.set(file)
                    
                    return
                    addToLogs(set_payment)
                    
                    if set_payment["hasError"]:
                        self.autoSetPaymentBtn.config(state="normal")
                        return msg.showerror("Payment", set_payment["content"]["ERROR"])
                        
                    add_payment = payment.add()
                    
                    if add_payment["hasError"]:
                        msg.showwarning("Payment", add_payment["content"])
                   
                    self.payment_info.config(
                        text=f'Paid: {set_payment["content"]["PAID"]} Colis - {set_payment["content"]["TRANSFERED_AMOUNT"]} Dhs - Date: {set_payment["content"]["TRANSFER_DATE"]}\nNot same price: {len(set_payment["content"]["NOT_SAME_AMOUNT"])}\nNot found: {len(set_payment["content"]["NOT_FOUND"])}\nExceed Shipping Fees: {len(set_payment["content"]["EXCEED_SHIPPING_FEES"])}'
                        )
                    
                    setLastPaymentDatetime(str(downloadAttachementResponse["content"]))
                    
                    ws.Beep(500,500)
                    
                    # push to github
                    autoPush(".", "backup shipments history")
                    
                    if set_payment["hasWarning"]:
                        msg.showwarning("Payment Warning", "Check logs")
                        os.system(f"notepad.exe {BASE_DIR}/logs/payment_logs.txt")
            
        except Exception as exception:
            msg.showerror("Payment Error", f"{exception},'\nerror line: ',{sys.exc_info()[-1].tb_lineno}")
       
        self.autoSetPaymentBtn.config(state="normal")
        
        
    def manualSetPayment(self):
        payment = Payment()
        set_payment = payment.set(self.filePath)
         
        addToLogs(set_payment)
        
        if set_payment["hasError"]:
            return msg.showerror("Payment", set_payment["content"]["ERROR"])
        
        if set_payment["hasWarning"]:
            msg.showwarning("Payment Warning", "Check logs")
            os.system(f"notepad.exe {BASE_DIR}/logs/payment_logs.txt")
            
        add_payment = payment.add()
        if add_payment["hasError"]:
            msg.showwarning("Payment Error", add_payment["content"])

        self.payment_info.config(text=f'Paid: {set_payment["content"]["PAID"]} Colis - {set_payment["content"]["TRANSFERED_AMOUNT"]} Dhs - Date: {set_payment["content"]["TRANSFER_DATE"]}\nNot same price: {set_payment["content"]["NOT_SAME_AMOUNT"]}\nNot found: {set_payment["content"]["NOT_FOUND"]}\nExceed Shipping Fees: {set_payment["content"]["EXCEED_SHIPPING_FEES"]}')
        ws.Beep(500,500)
        # push to github
        autoPush(".", "backup shipments history")
        

    def updateOrdersStatus(self):
        self.tools_menu.entryconfig(0, state="disabled")
        orders = HandleJsonFiles.read(self.json_files['orders'])
        if orders:
            total_orders = len(orders)
            self.progress.pack()
            successed = failed = 0
            processed = 1
            for order_id, store in orders.items():
                self.update_idletasks()
                self.progress['value'] += 100/total_orders
                if "cmd" not in order_id:
                    script_response = PrestashopAPI.updateOrderStatus(store, order_id)
                    self.stateLabel.config(text=script_response)
                    if 'Encours de livraison' not in script_response:
                        failed += 1
                    else:
                        successed += 1
                        HandleJsonFiles.delete(order_id, self.json_files['orders'])
                        
                    self.stateLabel.config(text=f'{processed}/{total_orders} - {script_response}')
                else:
                    successed += 1
                    self.stateLabel.config(text=f'{processed}/{total_orders} : Order Whatsapp')
                    HandleJsonFiles.delete(order_id, self.json_files['orders'])
                    
                processed += 1

            self.progress.stop()
            self.progress.pack_forget()
            self.stateLabel.config(text=f'{successed} status updated\n{failed} status not updated')
            
            self.totalIDs.config(text=f"Total: {len(HandleJsonFiles.read(self.json_files['orders']))}")
            
            self.totalCmdReady.config(text=f"Ready to print: {len(HandleJsonFiles.read(self.json_files['shipmentsNumbers']))}")
            
            autoPush(".", "backup shipments history")

        else:
            msg.showinfo('Update Status', 'No orders found') 
            
        self.ID.focus()
        self.tools_menu.entryconfig(0, state="normal")


    def autoCreateShipment(self):
        try:
            # remove non numerical characters
            ORDER_ID = re.sub('[^0-9]', '', self.ID.get())
            
            if not ORDER_ID:
                return msg.showerror('Tawssil','Missing Order ID')
            
            if Checker.order_added(ORDER_ID):
                if not msg.askyesno("Tawssil", f"had CMD N°{ORDER_ID} deja dkhltiha, baghi t3awdha ?"):
                    return self.resetEntries(self.packageCreationFrame)
            
            shipped = Checker.order_shipped(ORDER_ID)
            if shipped and not msg.askyesno("Tawssil", f"had CMD N°{ORDER_ID} deja kherjat le {shipped} , baghi t3awdha ?"):
                    return self.resetEntries(self.packageCreationFrame)
            
            if Checker.old_order(self.store_selected.get(), ORDER_ID):
                ws.Beep(900,700)
                if not msg.askyesno("Tawssil", f"had cmd {ORDER_ID} raha 9dima f {self.store_selected.get()}\n\nyla kant f chi site akhor clique Non w bdl site\n\nyla baghi dkhlha clique Oui"):
                    return

            self.enableDisableWidgets([self.packageCreationFrame])
            
            self.stateLabel.config(text="Getting order data...")
            order_data = PrestashopAPI.orderData(self.store_selected.get() ,ORDER_ID)

            if type(order_data) == dict:
                order_data["delivery_type"] = self.type_selected.get()

                Formatter.changed_fields(order_data, self.getManualFields())

                if not order_data["phone1"]:
                    self.enableDisableWidgets([self.packageCreationFrame])
                    return msg.showerror("Phone", f"invalid phone => {order_data['phone1']}")
                
                if Checker.is_casablanca(order_data["city"]):
                    if not msg.askyesno("Tawssil", f"had cmd dayra {order_data['city'].title()} yla baghi dkhloha clique sur oui"):
                        return self.enableDisableWidgets([self.packageCreationFrame])

                total_returned = Checker.total_returned(order_data["phone1"])
                if total_returned:
                    msg.showwarning("Warning", f"Client deja 3ndha {total_returned} cmd retour (ghadi dkhel baghi thaydha dir liha annuler)")
                    webbrowser.open(f"http://livraison.horscasa:8010/shipments/history/{order_data['phone1']}")
                    
                if order_data["delivery_type"] == "Return":
                    order_data["total"] = 0
                
                self.stateLabel.config(text="Creating package...")

                response = TawssilAPI.createPackage(order_data, order_data["delivery_type"])

                if not response["hasError"]:
                    shipmentNumber = response["content"]

                    HandleJsonFiles.saveToHistory(shipmentNumber ,order_data, ORDER_ID)

                    self.totalIDs.config(text=f"Total:  {len(HandleJsonFiles.read(self.json_files['orders']))}")
                    self.totalCmdReady.config(text=f"Ready to print: {len(HandleJsonFiles.read(self.json_files['shipmentsNumbers']))}")
                    
                    self.enableDisableWidgets([self.packageCreationFrame])
                    self.resetEntries(self.packageCreationFrame)    
                    ws.Beep(500,500)
                    
                    # print labels when reaching total shipments in the settings (see json_files/settings.json)
                    if Settings.autoPrint() and Settings.totalToPrintAuto() == len(HandleJsonFiles.read(self.json_files['shipmentsNumbers'])):
                        self.stateLabel.config(text="Printing...")
                        Thread(target=self.printLabels, args=("auto",)).start()

                    self.stateLabel.config(text=f'{order_data["store"].title() if not order_data["store"].startswith("ww") else order_data["store"].title()[4:]}: N°{ORDER_ID}\n{order_data["name"]}\n{order_data["phone1"]}  {order_data["phone2"] if order_data["phone2"] != order_data["phone1"] else ""}\n{order_data["city"]}\n{order_data["total"]} DHs')
                    
                    return

                elif response["content"] == "one or many of the cities provided are invalid":
                    msg.showerror("City Error", f"<{order_data['city']}> had lmdina ya imma makinach ya imma mamktobach mzn\nyla l9itiha ktebha manuel")
                    webbrowser.open("http://livraison.horscasa:8010/tawssil_cities/")
                    self.stateLabel.config(text=f"invalid city <{order_data['city']}>")
                else:
                    msg.showerror("Error", response["content"])
                    self.stateLabel.config(text=response["content"])
                
            else:
                msg.showerror("PrestashopAPI", order_data)
                self.stateLabel.config(text=order_data)
        
        except Exception as e:
            msg.showerror("Error", f'{e}\nerror line: {sys.exc_info()[-1].tb_lineno}')
            self.stateLabel.config(text=f'{e}\nerror line: {sys.exc_info()[-1].tb_lineno}')
        
        self.enableDisableWidgets([self.packageCreationFrame])


    def manualCreateShipment(self):
        '''
        Post order data manually into Tawssil via API
        '''
        try:
            if not self.getManualFields()["name"] or type(self.getManualFields()["total"]) != int  or not self.getManualFields()["city"].strip() or not self.getManualFields()["address"].strip():
                return msg.showerror("Data", "Missing some fields")

            if not Formatter.phone(self.getManualFields()["phone"]):
                return msg.showerror("Phone invalide", f"Invalid Phone\n\n{self.getManualFields()['phone']}")

            self.enableDisableWidgets([self.packageCreationFrame])

            store = self.store_selected.get()

            order_data = {
                'deliveryCompany': "Tawssil",
                'delivery_type': self.type_selected.get(),
                'id': "",
                'store': store,
                'created': f"{date.today()}",
                "shipped": f"{date.today()}",
                "delivered": "",
                "period": "",
                "delay": "",
                'name': self.getManualFields()["name"],
                'address': self.getManualFields()["address"],
                'city': self.getManualFields()["city"].lower(),
                'phone1': self.getManualFields()["phone"],
                'phone2': self.getManualFields()["phone"],
                'total': int(self.getManualFields()["total"]),
                'status': "SHIPPED",
                'last_status' : "",
                'remark': self.getManualFields()["remark"]
                }
                        
            if order_data["delivery_type"] == "Return":
                order_data["total"] = 0
                
            self.stateLabel.config(text="Creating package...")
            response = TawssilAPI.createPackage(order_data, order_data["delivery_type"])
        
            if not response["hasError"]:
                shipmentNumber = response["content"]

                HandleJsonFiles.saveToHistory(shipmentNumber, order_data, f"cmd{self.getManualFields()['phone']}")

                self.totalIDs.config(text=f"Total: {len(HandleJsonFiles.read(self.json_files['orders']))}")   
                self.totalCmdReady.config(text=f"Ready to print: {len(HandleJsonFiles.read(self.json_files['shipmentsNumbers']))}")  
                 # Notify & Clear/Reset fields
                self.enableDisableWidgets([self.packageCreationFrame])
                self.resetEntries(self.packageCreationFrame)    
                ws.Beep(500,500)
                # print labels when reaching total shipments in the settings (see json_files/settings.json)
                if Settings.autoPrint() and Settings.totalToPrintAuto() == len(HandleJsonFiles.read(self.json_files['shipmentsNumbers'])):
                    self.stateLabel.config(text="Printing...")
                    Thread(target=self.printLabels, args=("auto",)).start()

                self.stateLabel.config(text=f'{store}-Whatsapp\n{order_data["name"]}\n{order_data["phone1"]}\n{order_data["city"]}\n{order_data["total"]} DHs')

                return
            
            elif response["content"] == "one or many of the cities provided are invalid":
                msg.showerror("City Error", f"<{order_data['city']}> had lmdina ya imma makinach ya imma mamktobach mzn")
                webbrowser.open("http://livraison.horscasa:8010/tawssil_cities/")
                self.stateLabel.config(text=f"invalid city <{order_data['city']}>")
                    
            else:
                msg.showerror("Error", response["content"])
                self.stateLabel.config(text=response["content"])

        except Exception as e:
            msg.showerror("Error", f'{e}\nerror line: {sys.exc_info()[-1].tb_lineno}')
            self.stateLabel.config(text=f'{e}\nerror line: {sys.exc_info()[-1].tb_lineno}')

        self.enableDisableWidgets([self.packageCreationFrame])


    def downloadLabels(self, shipmentsNumbers):
        try:
            emptyDirectory("labels")

            if not shipmentsNumbers:
                return msg.showinfo("Labels", "No Packages found")

            for shipmentNumber in shipmentsNumbers:
                response = TawssilAPI.generateLabel(shipmentNumber)

                if not response["hasError"]:
                    HandlePdfFiles.download(response["content"], Path(f"labels/{shipmentNumber}.pdf"))
               
                    self.download_label.config(text=f"{shipmentsNumbers.index(shipmentNumber)+1}/{len(shipmentsNumbers)} : {shipmentNumber}")
                    
                    HandleJsonFiles.delete(f"Shipment{shipmentNumber}", self.json_files['shipmentsNumbers'])
                else:                   
                    self.download_label.config(text=f"{shipmentsNumbers.index(shipmentNumber)+1}/{len(shipmentsNumbers)} : {shipmentNumber} - {response['content']}")

        except Exception as e:
            msg.showerror("Error", f'{e}\nerror line: {sys.exc_info()[-1].tb_lineno}')
            
            
    def printLabels(self, method):
        self.enableDisableWidgets([self.packageCreationFrame, self.package_info_frame]) 
        try:
            if method == "manual":
                shipments_numbers_entry = re.sub("[^0-9,]", "", self.shipments_numbers.get())
                shipments_numbers = shipments_numbers_entry.split(",") if shipments_numbers_entry else []
                self.downloadLabels(shipments_numbers)
                self.shipments_numbers.delete(0, "end")
            else:
                shipments_numbers = list(HandleJsonFiles.read(self.json_files['shipmentsNumbers']).values())
                self.downloadLabels(shipments_numbers)
                self.totalIDs.config(text=f"Total: {len(HandleJsonFiles.read(self.json_files['orders']))}")
                self.totalCmdReady.config(text=f"Ready to print: {len(HandleJsonFiles.read(self.json_files['shipmentsNumbers']))}")
            
            if len(shipments_numbers) == 1:
                pdf_file = os.listdir(f"{BASE_DIR}/labels")[0]
                HandlePdfFiles.print(f"{BASE_DIR}/labels/{pdf_file}")
            elif len(shipments_numbers) > 1:
                merging_result = HandlePdfFiles.merge(f"{BASE_DIR}/labels")

                if merging_result.endswith("pdf"):
                    HandlePdfFiles.print(merging_result)
                else:
                    msg.showerror("PDF Merger", merging_result)
                    
        except Exception as e:
            msg.showerror("Error", f'{e}\nerror line: {sys.exc_info()[-1].tb_lineno}')
            
            
        self.enableDisableWidgets([self.packageCreationFrame, self.package_info_frame]) 
    
        self.ID.focus()


    def updatePackage(self):
        try:
            history = HandleJsonFiles.read("history/shipmentsHistory")
            
            packageNumber = re.sub('[^0-9]', '', self.packageNumber.get())
            newPhone = re.sub('[^0-9]', '', self.newPhone.get())
            newAmount = re.sub('[^0-9]', '', self.newAmount.get())
            
            if not packageNumber:
                return msg.showerror("Validation", "Missing Package Number")
            
            if packageNumber not in history:
                return msg.showerror("404", f"{packageNumber} not found")
            
            if not any([newPhone, newAmount]):
                return msg.showerror("Validation", "minimum 1 field required")
            
            newData = {}
            
            if newPhone:
                if not Formatter.phone(newPhone):
                    return msg.showerror("Validation", f"Invalid phone <{newPhone}>")
                
                newData["phone"] = newPhone
                
            if newAmount: newData["cash_on_delivery"] = int(newAmount)
            
            response = TawssilAPI.updatePackage(packageNumber, newData)
            
            if response["hasError"]:
                return msg.showerror("Update Package Error", response["content"])
            
            history[packageNumber]["phone1"] = newPhone
            history[packageNumber]["total"] = int(newAmount)
            
            HandleJsonFiles.edit(history, "history/shipmentsHistory") 
                    
            msg.showinfo("Success", "Package has been updated\nre-print the label again")
            
            self.packageNumber.delete(0, "end")
            self.newPhone.delete(0, "end")
            self.newAmount.delete(0, "end")
            
        except Exception as exception:
            msg.showerror("Error", f"Package update failed\n\nError:\n{exception}")
        
        
    def refund(self):
        """
        Add refund to refund web app via API
        """
        ORDER_ID = re.sub('[^0-9]', '', self.ID.get())
        ORDER_AMOUNT = re.sub('[^0-9]', '', self.price.get())

        if not ORDER_ID or not ORDER_AMOUNT:
            return msg.showerror('Refund', 'Missing Order ID/Amount')
        
        store = self.store_selected.get()
        
        order_data = PrestashopAPI.orderData(store ,ORDER_ID)

        if type(order_data) != dict:
            return msg.showerror("PrestashopAPI", order_data)
        
        data = {
            "order_id": f"{ORDER_ID}-{store}",
            "name": order_data["name"],
            "amount": int(ORDER_AMOUNT),
            "order_date": order_data["created"]
        }

        if order_data["total"] != 0:
            if not msg.askyesno("Refund", f"had cmd mamkhalsach en ligne, mt2kd baghi t ajouter remboursement ?"):
                return

        addRefund = ParaApi.add_refund(data)

        try:
            if not addRefund.json()["created"]:
                return msg.showwarning("Refund", addRefund.json()["error"])
            
            self.stateLabel.config(text=f'Refund Added-Order-N°{ORDER_ID}-{store}-{ORDER_AMOUNT} Dhs')
            self.resetEntries(self.packageCreationFrame) 
            ws.Beep(500,500)
       
        except Exception as exception:
            msg.showerror("Refund", f"Error:\n\n{exception}")
            
            
    def launchApp(self):
        HandleJsonFiles.create([ self.json_files["orders"], self.json_files["shipmentsNumbers"] ])
        self.Widgets()
        self.mainloop()
        

app = TawssilApp()

if __name__ == '__main__':
    app.launchApp()