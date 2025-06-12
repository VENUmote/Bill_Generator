function addRow() {
            const table = document.getElementById("items-table").getElementsByTagName('tbody')[0];
            const newRow = table.insertRow();
            for (let i = 0; i < 6; i++) {
                const cell = newRow.insertCell(i);
                const input = document.createElement("input");
                input.type = "text";
                input.placeholder = i === 4 ? "Quantity" : i === 5 ? "Rate" : (i === 2 ? "GST Percentage" : "Item Name");
                cell.appendChild(input);
            }
            const removeCell = newRow.insertCell(6);
            const removeBtn = document.createElement("span");
            removeBtn.classList.add("remove-row-btn");
            removeBtn.innerText = "X";
            removeBtn.onclick = function () { removeRow(removeBtn); };
            removeCell.appendChild(removeBtn);
        }

        function removeRow(btn) {
            const row = btn.parentElement.parentElement;
            row.remove();
        }
        flatpickr("#id_invoice_date", {
            dateFormat: "Y-m-d",       // Ensures correct date format
            defaultDate: "today"       // Sets today's date as default
        });
        
        flatpickr("#id_date_of_despatch", {
            dateFormat: "Y-m-d",       // Ensures correct date format
            defaultDate: "today"       // Sets today's date as default
        });
        

        const today = new Date().toISOString().split('T')[0];
            document.getElementById('id_invoice_date').value = today;






        function addRow() {
            let table = document.getElementById("items-table").getElementsByTagName('tbody')[0];
            let rowCount = table.rows.length + 1;
            
            let newRow = table.insertRow();
            newRow.innerHTML = `
                <input type="hidden" name="item_id" value="">
                <td><input type="text" name="item_name" required></td>
                <td><input type="text" name="hsn_code" required></td>
                <td>
                    <select name="gst_percentage" required>
                        <option value="18">18%</option>
                        <option value="5">5%</option>
                    </select>
                </td>
                <td><input type="text" name="uom" required></td>
                <td><input type="number" name="quantity" required></td>
                <td><input type="number" name="rate" required></td>
                <td><span class="remove-row-btn" onclick="removeRow(this)">Remove</span></td>
            `;
        }
        function removeRow(button) {
                let row = button.closest("tr");
                row.remove();
            }
    
