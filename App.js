import { useEffect, useState } from 'react'
import './App.css'

export default function App() {
  // Load data from LocalStorage on startup
  const [employees, setEmployees] = useState(() => {
    const saved = localStorage.getItem('employees')
    return saved ? JSON.parse(saved) : []
  })

  const [expenses, setExpenses] = useState(() => {
    const saved = localStorage.getItem('expenses')
    return saved ? JSON.parse(saved) : []
  })

  // Input states
  const [newEmpName, setNewEmpName] = useState('')
  const [newEmpEmail, setNewEmpEmail] = useState('')
  const [newEmpSalary, setNewEmpSalary] = useState('')

  const [newExpDesc, setNewExpDesc] = useState('')
  const [newExpAmount, setNewExpAmount] = useState('')
  const [newExpCategory, setNewExpCategory] = useState('Salary')

  const [activeTab, setActiveTab] = useState('dashboard')

  // Auto-save to LocalStorage whenever data changes
  useEffect(() => {
    localStorage.setItem('employees', JSON.stringify(employees))
  }, [employees])

  useEffect(() => {
    localStorage.setItem('expenses', JSON.stringify(expenses))
  }, [expenses])

  // --- EMPLOYEE FUNCTIONS ---
  const addEmployee = () => {
    if (!newEmpName || !newEmpSalary) {
      alert('Please fill Name and Salary!')
      return
    }
    
    const newEmployee = {
      id: Date.now() + Math.random(), // Unique ID
      name: newEmpName,
      email: newEmpEmail || '-',
      salary: parseFloat(newEmpSalary)
    }

    // Update state immediately
    setEmployees([newEmployee, ...employees])
    
    // Clear form
    setNewEmpName('')
    setNewEmpEmail('')
    setNewEmpSalary('')
  }

  const deleteEmployee = (id) => {
    // Filter out the employee with the specific ID
    const updatedList = employees.filter(emp => emp.id !== id)
    setEmployees(updatedList)
  }

  // --- EXPENSE FUNCTIONS ---
  const addExpense = () => {
    if (!newExpDesc || !newExpAmount) {
      alert('Please fill Description and Amount!')
      return
    }

    const newExpense = {
      id: Date.now() + Math.random(), // Unique ID
      description: newExpDesc,
      amount: parseFloat(newExpAmount),
      category: newExpCategory,
      date: new Date().toISOString()
    }

    setExpenses([newExpense, ...expenses])

    setNewExpDesc('')
    setNewExpAmount('')
    setNewExpCategory('Salary')
  }

  const deleteExpense = (id) => {
    const updatedList = expenses.filter(exp => exp.id !== id)
    setExpenses(updatedList)
  }

  // --- DASHBOARD CALCULATIONS ---
  // These run automatically every time 'employees' or 'expenses' state changes
  const getTotalSalaries = () => employees.reduce((sum, emp) => sum + (emp.salary || 0), 0)
  const getTotalExpenses = () => expenses.reduce((sum, exp) => sum + (exp.amount || 0), 0)
  
  // Logic: Net Pay = Total Salaries - 15% Tax (Simulated Revenue)
  const getNetPay = () => getTotalSalaries() - (getTotalSalaries() * 0.15)
  
  const getHealthScore = () => {
    const income = getTotalSalaries()
    if (income === 0) return 50
    const score = 100 - (getTotalExpenses() / income) * 100
    return Math.round(Math.max(0, Math.min(100, score)))
  }

  const getRunway = () => {
    const burn = getTotalExpenses()
    return burn === 0 ? 0 : Math.round((getNetPay() / burn) * 10) / 10
  }

  const getGrade = () => {
    const score = getHealthScore()
    if (score >= 80) return 'A'
    if (score >= 60) return 'B'
    if (score >= 40) return 'C'
    return 'F'
  }

  const getExpensesByCategory = () => {
    const grouped = {}
    expenses.forEach(exp => {
      grouped[exp.category] = (grouped[exp.category] || 0) + exp.amount
    })
    return Object.entries(grouped).map(([cat, amt]) => ({ category: cat, amount: amt }))
  }

  return (
    <div className="app-wrapper">
      {/* SIDEBAR */}
      <aside className="sidebar">
        <div className="logo">FinSage</div>
        <nav className="nav-menu">
          <button
            className={`nav-link ${activeTab === 'dashboard' ? 'active' : ''}`}
            onClick={() => setActiveTab('dashboard')}
          >
            <span>📊</span> Dashboard
          </button>
          <button
            className={`nav-link ${activeTab === 'employees' ? 'active' : ''}`}
            onClick={() => setActiveTab('employees')}
          >
            <span>👥</span> Employees
          </button>
          <button
            className={`nav-link ${activeTab === 'expenses' ? 'active' : ''}`}
            onClick={() => setActiveTab('expenses')}
          >
            <span>💸</span> Expenses
          </button>
          <button
            className={`nav-link ${activeTab === 'reports' ? 'active' : ''}`}
            onClick={() => setActiveTab('reports')}
          >
            <span>📈</span> Reports
          </button>
          <button
            className={`nav-link ${activeTab === 'settings' ? 'active' : ''}`}
            onClick={() => setActiveTab('settings')}
          >
            <span>⚙️</span> Settings
          </button>
        </nav>
      </aside>

      {/* MAIN CONTENT */}
      <main className="main-wrapper">
        <header className="top-header">
          <div>
            <p className="welcome">Welcome back</p>
            <h1 className="company">TechStart Inc.</h1>
          </div>
          <div className="notification">🔔</div>
        </header>

        <div className="content-area">
          {/* DASHBOARD TAB */}
          {activeTab === 'dashboard' && (
            <div className="dashboard-content">
              <div className="dashboard-grid">
                {/* HEALTH CARD */}
                <div className="health-card-large">
                  <h3>Financial Health</h3>
                  <div className="health-display">
                    <div className="score-section">
                      <div className="score-big">{getHealthScore()}</div>
                      <div className="score-label">/100</div>
                    </div>
                    <div className={`grade-badge grade-${getGrade()}`}>
                      {getGrade()}
                    </div>
                  </div>
                </div>

                {/* KPI CARDS */}
                <div className="kpi-card">
                  <div className="kpi-icon">📈</div>
                  <div className="kpi-label">Projected Revenue</div>
                  <div className="kpi-value">₹{getTotalSalaries().toLocaleString()}</div>
                </div>

                <div className="kpi-card">
                  <div className="kpi-icon">📉</div>
                  <div className="kpi-label">Total Expenses</div>
                  <div className="kpi-value">₹{getTotalExpenses().toLocaleString()}</div>
                </div>

                <div className="kpi-card">
                  <div className="kpi-icon">💰</div>
                  <div className="kpi-label">Net Income (Est)</div>
                  <div className="kpi-value">₹{getNetPay().toLocaleString()}</div>
                </div>
              </div>

              {/* SECONDARY METRICS */}
              <div className="metrics-section">
                <div className="metric-card">
                  <div className="metric-icon">⏳</div>
                  <div className="metric-title">Runway</div>
                  <div className="metric-big">{getRunway()}</div>
                  <div className="metric-label">months left</div>
                </div>

                <div className="metric-card">
                  <div className="metric-icon">🔥</div>
                  <div className="metric-title">Burn Rate</div>
                  <div className="metric-big">₹{getTotalExpenses().toLocaleString()}</div>
                  <div className="metric-label">per month</div>
                </div>

                <div className="metric-card">
                  <div className="metric-icon">💾</div>
                  <div className="metric-title">Savings Rate</div>
                  <div className="metric-big">{getTotalSalaries() > 0 ? ((getNetPay() / getTotalSalaries()) * 100).toFixed(1) : 0}%</div>
                  <div className="metric-label">of revenue</div>
                </div>

                <div className="metric-card">
                  <div className="metric-icon">👥</div>
                  <div className="metric-title">Team Size</div>
                  <div className="metric-big">{employees.length}</div>
                  <div className="metric-label">active employees</div>
                </div>
              </div>

              {/* ALERTS */}
              {employees.length > 0 && (
                <div className="alert-banner">
                  <div className="alert-content">
                    <div className="alert-icon">⚠️</div>
                    <div>
                      <div className="alert-title">Payroll Pending</div>
                      <div className="alert-text">{employees.length} employees • ₹{getTotalSalaries().toLocaleString()}</div>
                    </div>
                  </div>
                  <div className="alert-arrow">→</div>
                </div>
              )}

              {/* AI INSIGHTS */}
              <div className="insights-card">
                <h3>💡 AI Insights</h3>
                <p>
                  {getHealthScore() < 40 ? (
                    '⚠️ Your expenses are high compared to revenue. Consider cost optimization immediately.'
                  ) : getHealthScore() > 80 ? (
                    '✅ Great financial health! You are managing expenses very efficiently.'
                  ) : (
                    '📊 Your financial health is moderate. Keep an eye on rising miscellaneous expenses.'
                  )}
                </p>
                {expenses.length > 0 && (
                  <p>
                    💾 Highest spending category: <strong>{getExpensesByCategory().sort((a, b) => b.amount - a.amount)[0]?.category}</strong>
                  </p>
                )}
              </div>
            </div>
          )}

          {/* EMPLOYEES TAB */}
          {activeTab === 'employees' && (
            <div className="tab-content">
              <h2>Manage Employees</h2>
              
              <div className="form-section">
                <h3>Add New Employee</h3>
                <div className="form-grid">
                  <input
                    placeholder="Employee Name"
                    value={newEmpName}
                    onChange={(e) => setNewEmpName(e.target.value)}
                    className="form-input"
                  />
                  <input
                    placeholder="Email"
                    value={newEmpEmail}
                    onChange={(e) => setNewEmpEmail(e.target.value)}
                    className="form-input"
                  />
                  <input
                    placeholder="Salary"
                    type="number"
                    value={newEmpSalary}
                    onChange={(e) => setNewEmpSalary(e.target.value)}
                    className="form-input"
                  />
                  <button onClick={addEmployee} className="btn-primary">
                    ➕ Add Employee
                  </button>
                </div>
              </div>

              <div className="table-section">
                {employees.length === 0 ? (
                  <p className="empty-message">No employees yet</p>
                ) : (
                  <table className="data-table">
                    <thead>
                      <tr>
                        <th>Name</th>
                        <th>Email</th>
                        <th>Salary</th>
                        <th>Action</th>
                      </tr>
                    </thead>
                    <tbody>
                      {employees.map(emp => (
                        <tr key={emp.id}>
                          <td>{emp.name}</td>
                          <td>{emp.email}</td>
                          <td>₹{parseInt(emp.salary).toLocaleString()}</td>
                          <td>
                            <button
                              onClick={() => deleteEmployee(emp.id)}
                              className="btn-delete"
                            >
                              Delete
                            </button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                )}
              </div>
            </div>
          )}

          {/* EXPENSES TAB */}
          {activeTab === 'expenses' && (
            <div className="tab-content">
              <h2>Manage Expenses</h2>
              
              <div className="form-section">
                <h3>Add New Expense</h3>
                <div className="form-grid">
                  <input
                    placeholder="Description"
                    value={newExpDesc}
                    onChange={(e) => setNewExpDesc(e.target.value)}
                    className="form-input"
                  />
                  <input
                    placeholder="Amount"
                    type="number"
                    value={newExpAmount}
                    onChange={(e) => setNewExpAmount(e.target.value)}
                    className="form-input"
                  />
                  <select
                    value={newExpCategory}
                    onChange={(e) => setNewExpCategory(e.target.value)}
                    className="form-input"
                  >
                    <option value="Salary">Salary</option>
                    <option value="Rent">Rent</option>
                    <option value="Utilities">Utilities</option>
                    <option value="Software">Software</option>
                    <option value="Marketing">Marketing</option>
                    <option value="Travel">Travel</option>
                    <option value="Equipment">Equipment</option>
                    <option value="Other">Other</option>
                  </select>
                  <button onClick={addExpense} className="btn-primary">
                    ➕ Add Expense
                  </button>
                </div>
              </div>

              <div className="table-section">
                {expenses.length === 0 ? (
                  <p className="empty-message">No expenses yet</p>
                ) : (
                  <table className="data-table">
                    <thead>
                      <tr>
                        <th>Description</th>
                        <th>Category</th>
                        <th>Amount</th>
                        <th>Action</th>
                      </tr>
                    </thead>
                    <tbody>
                      {expenses.map(exp => (
                        <tr key={exp.id}>
                          <td>{exp.description}</td>
                          <td><span className="badge">{exp.category}</span></td>
                          <td>₹{parseInt(exp.amount).toLocaleString()}</td>
                          <td>
                            <button
                              onClick={() => deleteExpense(exp.id)}
                              className="btn-delete"
                            >
                              Delete
                            </button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                )}
              </div>
            </div>
          )}

          {/* REPORTS TAB */}
          {activeTab === 'reports' && (
            <div className="tab-content">
              <h2>Financial Reports</h2>
              
              <div className="reports-grid">
                <div className="report-card">
                  <h3>Income Summary</h3>
                  <div className="report-item">
                    <span>Total Salaries</span>
                    <span>₹{getTotalSalaries().toLocaleString()}</span>
                  </div>
                  <div className="report-item">
                    <span>Deductions (15%)</span>
                    <span>₹{(getTotalSalaries() * 0.15).toLocaleString()}</span>
                  </div>
                  <div className="report-item highlight">
                    <span>Net Income</span>
                    <span>₹{getNetPay().toLocaleString()}</span>
                  </div>
                </div>

                <div className="report-card">
                  <h3>Expense Breakdown</h3>
                  {getExpensesByCategory().length === 0 ? (
                    <p>No expenses recorded</p>
                  ) : (
                    <>
                      {getExpensesByCategory().map((cat, idx) => (
                        <div key={idx} className="report-item">
                          <span>{cat.category}</span>
                          <span>₹{cat.amount.toLocaleString()}</span>
                        </div>
                      ))}
                      <div className="report-item highlight">
                        <span>Total</span>
                        <span>₹{getTotalExpenses().toLocaleString()}</span>
                      </div>
                    </>
                  )}
                </div>

                <div className="report-card">
                  <h3>Metrics</h3>
                  <div className="report-item">
                    <span>Financial Health</span>
                    <span>{getHealthScore()}/100</span>
                  </div>
                  <div className="report-item">
                    <span>Runway</span>
                    <span>{getRunway()} months</span>
                  </div>
                  <div className="report-item">
                    <span>Team Size</span>
                    <span>{employees.length} employees</span>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* SETTINGS TAB */}
          {activeTab === 'settings' && (
            <div className="tab-content">
              <h2>Settings</h2>
              
              <div className="settings-card">
                <div className="setting-item">
                  <span>App Version</span>
                  <span>FinSage 1.0 (Local)</span>
                </div>
                <div className="setting-item">
                  <span>Storage</span>
                  <span>Browser Local Storage</span>
                </div>
                <div className="setting-item">
                  <button 
                    onClick={() => {
                      if(window.confirm('Clear all data?')) {
                        setEmployees([]);
                        setExpenses([]);
                        localStorage.clear();
                      }
                    }} 
                    className="btn-delete"
                  >
                    Reset All Data
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>
      </main>
    </div>
  )
}
