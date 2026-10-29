import React, { useState } from 'react';
import Papa from 'papaparse';
import { jsPDF } from 'jspdf';
import { 
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, 
  PieChart, Pie, Cell 
} from 'recharts';

export default function App() {
  const [currentView, setCurrentView] = useState('login');
  const [currentUser, setCurrentUser] = useState(null);
  const [authMode, setAuthMode] = useState('signin'); // 'signin' or 'signup'
  
  // Login credentials state
  const [loginEmail, setLoginEmail] = useState('admin@edupredict.edu');
  const [loginPassword, setLoginPassword] = useState('Admin@2026');
  const [selectedRoleType, setSelectedRoleType] = useState('Admin'); 

  // Credential Store
  const [registeredUsers, setRegisteredUsers] = useState([
    { name: "Dr. P. David", email: "admin@edupredict.edu", role: "Admin", password: "Admin@2026" },
    { name: "S. R. Rao", email: "staff@edupredict.edu", role: "Admission Staff", password: "Staff@2026" },
    { name: "P. K. Varma", email: "counselor@edupredict.edu", role: "Academic Counselor", password: "Counselor@2026" }
  ]);

  // Signup form state
  const [signupForm, setSignupForm] = useState({
    name: '',
    email: '',
    role: 'Admission Staff',
    password: '',
    confirmPassword: ''
  });

  // App Data State
  const [students, setStudents] = useState([
    {
      id: "STU-2026-001",
      name: "Aarav Sharma",
      inter1Marks: 470,
      inter2Marks: 485,
      mathMarks: 98,
      physicsMarks: 95,
      chemMarks: 92,
      overallPercentage: 94.5,
      entranceScore: 920,
      board: "State Board",
      medium: "English",
      coaching: "Yes",
      preferredDegree: "B.Tech",
      preferredBranch: "Computer Science & Engineering",
      parentOccupation: "Engineer",
      householdIncome: 850000,
      predictedGPA: 9.1,
      performanceCategory: "High",
      supportNeeded: "None - Advanced Track Eligible",
      branchRecs: [
        { branch: "Computer Science & Engineering", fitScore: "98%", reason: "Exceptional math & entrance scores, highly aligned with tech track." },
        { branch: "Artificial Intelligence & Data Science", fitScore: "95%", reason: "Strong quantitative foundations." }
      ],
      scholarships: [
        { type: "Merit-Based", status: "Eligible", amount: "50% Tuition Waiver", criteria: "Above 90% aggregate & top 5% entrance." },
        { type: "Financial-Need", status: "Not Eligible", amount: "N/A", criteria: "Income threshold below ₹5,00,000." }
      ]
    },
    {
      id: "STU-2026-002",
      name: "Ananya Patel",
      inter1Marks: 410,
      inter2Marks: 420,
      mathMarks: 82,
      physicsMarks: 78,
      chemMarks: 85,
      overallPercentage: 83.2,
      entranceScore: 780,
      board: "CBSE",
      medium: "English",
      coaching: "No",
      preferredDegree: "B.Tech",
      preferredBranch: "Electronics & Communication",
      parentOccupation: "Teacher",
      householdIncome: 420000,
      predictedGPA: 8.2,
      performanceCategory: "Moderate",
      supportNeeded: "Peer tutoring in Physics & Calculus",
      branchRecs: [
        { branch: "Electronics & Communication", fitScore: "89%", reason: "Solid chemistry & math scores." }
      ],
      scholarships: [
        { type: "Merit-Based", status: "Not Eligible", amount: "N/A", criteria: "Requires 90%+ aggregate." },
        { type: "Financial-Need", status: "Eligible", amount: "₹40,000 Annual Grant", criteria: "Household income under ₹5,00,000." }
      ]
    }
  ]);

  const [currentPage, setCurrentPage] = useState(1);
  const rowsPerPage = 15;

  const [historicalDatasets, setHistoricalDatasets] = useState([
    { fileName: "2024_batch_final_records.csv", recordsCount: 1240, status: "Trained & Validated", accuracy: "91.4%", sampleRows: [
        { id: "HIST-2024-001", name: "Kiran Kumar", inter: "94%", math: 96, gpa: 9.2, status: "Passed" },
        { id: "HIST-2024-002", name: "Divya Reddy", inter: "88%", math: 84, gpa: 8.5, status: "Passed" }
      ] 
    }
  ]);

  const [activeDatasetView, setActiveDatasetView] = useState(null);
  const [settings, setSettings] = useState({
    universityName: "Aditya College of Engineering and Technology",
    academicYear: "2026-2027",
    enableAutoScholarship: true
  });

  const [newStaffForm, setNewStaffForm] = useState({ name: '', email: '', role: 'Admission Staff', password: '' });
  const [toast, setToast] = useState(null);

  const showToast = (message, type = 'success') => {
    setToast({ message, type });
    setTimeout(() => setToast(null), 4000);
  };

  const [regForm, setRegForm] = useState({
    id: `STU-2026-0${students.length + 1}`,
    name: '',
    inter1Marks: '',
    inter2Marks: '',
    mathMarks: '',
    physicsMarks: '',
    chemMarks: '',
    overallPercentage: '',
    entranceScore: '',
    board: 'State Board',
    medium: 'English',
    coaching: 'No',
    preferredDegree: 'B.Tech',
    preferredBranch: 'Computer Science & Engineering',
    parentOccupation: '',
    householdIncome: ''
  });
  const [formErrors, setFormErrors] = useState({});
  const [selectedStudent, setSelectedStudent] = useState(students[0]);
  const [searchTerm, setSearchTerm] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('All');

  const handleLogin = (e) => {
    e.preventDefault();
    const foundUser = registeredUsers.find(
      u => u.email.toLowerCase() === loginEmail.toLowerCase() && u.password === loginPassword
    );

    if (foundUser) {
      setCurrentUser(foundUser);
      setCurrentView('dashboard');
      showToast(`Welcome back, ${foundUser.name} (${foundUser.role})!`);
    } else {
      showToast('Invalid email or password. Please check credentials.', 'error');
    }
  };

  const handleSignup = (e) => {
    e.preventDefault();
    if (!signupForm.name || !signupForm.email || !signupForm.password) {
      showToast('Please fill in all required sign-up fields.', 'error');
      return;
    }
    if (signupForm.password !== signupForm.confirmPassword) {
      showToast('Passwords do not match.', 'error');
      return;
    }
    if (registeredUsers.some(u => u.email.toLowerCase() === signupForm.email.toLowerCase())) {
      showToast('An account with this email already exists.', 'error');
      return;
    }

    const newUser = {
      name: signupForm.name,
      email: signupForm.email,
      role: signupForm.role,
      password: signupForm.password
    };

    setRegisteredUsers([...registeredUsers, newUser]);
    setCurrentUser(newUser);
    setCurrentView('dashboard');
    showToast(`Account created successfully! Logged in as ${newUser.role}`);
  };

  const handleRegisterSubmit = (e) => {
    e.preventDefault();
    let errors = {};
    if (!regForm.name.trim()) errors.name = 'Student name is required.';
    if (!regForm.inter1Marks || regForm.inter1Marks < 0) errors.inter1Marks = 'Valid Inter 1st year marks required.';
    if (!regForm.inter2Marks || regForm.inter2Marks < 0) errors.inter2Marks = 'Valid Inter 2nd year marks required.';

    if (Object.keys(errors).length > 0) {
      setFormErrors(errors);
      showToast('Please enter valid student marks.', 'error');
      return;
    }
    setFormErrors({});

    // Dynamic calculations based on user input marks
    const i1 = parseFloat(regForm.inter1Marks) || 450;
    const i2 = parseFloat(regForm.inter2Marks) || 450;
    const totalInterMarks = i1 + i2;
    const calcPercentage = regForm.overallPercentage ? parseFloat(regForm.overallPercentage) : Number(((totalInterMarks / 1000) * 100).toFixed(1));

    const math = parseFloat(regForm.mathMarks) || 85;
    const physics = parseFloat(regForm.physicsMarks) || 80;
    const chem = parseFloat(regForm.chemMarks) || 80;
    const entrance = parseFloat(regForm.entranceScore) || 750;

    // Advanced dynamic GPA mapping based on entrance score & inter percentage
    let baseScoreFactor = ((calcPercentage / 100) * 0.5) + ((entrance / 1000) * 0.3) + (((math + physics + chem) / 300) * 0.2);
    let predGPA = parseFloat((6.0 + (baseScoreFactor * 3.8)).toFixed(1));
    if (predGPA > 10) predGPA = 10.0;
    if (predGPA < 6.0) predGPA = 6.2;

    let category = predGPA >= 8.5 ? 'High' : predGPA >= 7.2 ? 'Moderate' : 'Needs Support';
    let support = category === 'Needs Support' 
      ? 'Intensive remedial coaching in core subjects & faculty mentoring' 
      : category === 'Moderate' 
      ? 'Peer tutoring in Physics & Calculus recommended' 
      : 'None - Advanced Track Eligible';

    const income = parseFloat(regForm.householdIncome) || 600000;
    const meritEligible = predGPA >= 8.5 ? "Eligible" : "Not Eligible";
    const needEligible = income <= 500000 ? "Eligible" : "Not Eligible";

    const branchFit1 = Math.min(99, Math.floor(75 + (math * 0.15) + (entrance * 0.01)));
    const branchFit2 = Math.max(70, branchFit1 - 7);

    const newStudent = {
      ...regForm,
      inter1Marks: i1,
      inter2Marks: i2,
      mathMarks: math,
      physicsMarks: physics,
      chemMarks: chem,
      overallPercentage: calcPercentage,
      entranceScore: entrance,
      predictedGPA: predGPA,
      performanceCategory: category,
      supportNeeded: support,
      branchRecs: [
        { branch: regForm.preferredBranch, fitScore: `${branchFit1}%`, reason: `Strong alignment with entrance score (${entrance}) and math proficiency (${math}/100).` },
        { branch: regForm.preferredBranch === 'Computer Science & Engineering' ? 'Artificial Intelligence & Data Science' : 'Computer Science & Engineering', fitScore: `${branchFit2}%`, reason: "Compatible quantitative foundation and historical cohort pass rates." }
      ],
      scholarships: [
        { type: "Merit-Based", status: meritEligible, amount: meritEligible === 'Eligible' ? "50% Tuition Waiver" : "N/A", criteria: "Predicted GPA >= 8.5 or aggregate > 90%" },
        { type: "Financial-Need", status: needEligible, amount: needEligible === 'Eligible' ? "₹40,000 Annual Grant" : "N/A", criteria: "Household income threshold <= ₹5,00,000" }
      ]
    };

    setStudents([newStudent, ...students]);
    showToast('Student registered and ML analysis generated successfully!');
    setSelectedStudent(newStudent);
    setCurrentView('report');
  };

  const handleRealCSVUpload = (e) => {
    if (currentUser?.role !== 'Admin') {
      showToast('Access Denied: Only Administrators can upload CSV datasets.', 'error');
      e.target.value = '';
      return;
    }
    const file = e.target.files?.[0];
    if (!file) return;

    Papa.parse(file, {
      header: true,
      skipEmptyLines: true,
      complete: ({ data, errors, meta }) => {
        const fields = meta.fields || [];
        const findValue = (row, aliases) => {
          const matchingField = fields.find((field) => aliases.includes(field.trim().toLowerCase()));
          return matchingField ? row[matchingField] : '';
        };
        const sampleRows = data.slice(0, 10).map((row, index) => {
          const id = findValue(row, ['id', 'student_id', 'student id', 'roll_no', 'roll number']);
          const name = findValue(row, ['name', 'student_name', 'student name', 'full_name', 'full name']);
          const inter = findValue(row, ['inter', 'inter_percentage', 'percentage', 'overall_percentage', 'overall percentage', 'aggregate']);
          const math = findValue(row, ['math', 'maths', 'math_marks', 'mathematics']);
          const gpa = findValue(row, ['gpa', 'predictedgpa', 'predicted_gpa', 'cgpa', 'result']);
          const status = findValue(row, ['status', 'result_status', 'outcome']);
          return {
            id: String(id || `CSV-${String(index + 1).padStart(3, '0')}`),
            name: String(name || `Record ${index + 1}`),
            inter: inter === '' ? '—' : String(inter),
            math: math === '' ? '—' : String(math),
            gpa: gpa === '' ? '—' : String(gpa),
            status: String(status || 'Imported')
          };
        });
        const newDataset = {
          fileName: file.name,
          recordsCount: data.length,
          status: errors.length ? 'Imported with warnings' : 'Imported (demo only)',
          accuracy: 'Not trained',
          sampleRows
        };
        setHistoricalDatasets((previous) => [newDataset, ...previous]);
        showToast(
          data.length
            ? `Imported ${data.length} CSV records. This demo does not train an ML model.`
            : 'No data rows were found in that CSV file.',
          data.length ? 'success' : 'error'
        );
        e.target.value = '';
      },
      error: () => {
        showToast('Could not read the CSV file. Please check its format.', 'error');
        e.target.value = '';
      }
    });
  };

  const exportStudentCsv = (student) => {
    const rows = [
      ['Field', 'Value'],
      ['Student ID', student.id],
      ['Name', student.name],
      ['Inter 1st Year Marks', student.inter1Marks],
      ['Inter 2nd Year Marks', student.inter2Marks],
      ['Math Marks', student.mathMarks],
      ['Physics Marks', student.physicsMarks],
      ['Chemistry Marks', student.chemMarks],
      ['Overall Percentage', student.overallPercentage],
      ['Entrance Exam Score', student.entranceScore],
      ['Preferred Branch', student.preferredBranch],
      ['Predicted GPA (demo heuristic)', student.predictedGPA],
      ['Performance Category', student.performanceCategory],
      ['Support Recommendation', student.supportNeeded],
      ...((student.branchRecs || []).map((rec, index) => [`Branch Recommendation ${index + 1}`, `${rec.branch} - ${rec.fitScore} - ${rec.reason}`])),
      ...((student.scholarships || []).map((sc, index) => [`Scholarship ${index + 1}`, `${sc.type}: ${sc.status}; ${sc.amount}; ${sc.criteria}`]))
    ];
    const csv = rows.map((row) => row.map((value) => `"${String(value ?? '').replace(/"/g, '""')}"`).join(',')).join('\r\n');
    const url = URL.createObjectURL(new Blob([csv], { type: 'text/csv;charset=utf-8;' }));
    const link = document.createElement('a');
    link.href = url;
    link.download = `${student.id || 'student'}_report.csv`;
    document.body.appendChild(link);
    link.click();
    link.remove();
    URL.revokeObjectURL(url);
    showToast(`CSV report downloaded for ${student.name}.`);
  };

  const exportStudentPdf = (student) => {
    const doc = new jsPDF();
    const left = 16;
    const maxWidth = 178;
    let y = 18;
    doc.setFont('helvetica', 'bold');
    doc.setFontSize(18);
    doc.text('EduPredict AI — Student Report', left, y);
    y += 10;
    doc.setFont('helvetica', 'normal');
    doc.setFontSize(10);
    doc.text(`Generated on ${new Date().toLocaleDateString()}`, left, y);
    y += 10;

    const reportLines = [
      `Student ID: ${student.id}`,
      `Student Name: ${student.name}`,
      `Preferred Branch: ${student.preferredBranch || 'Not specified'}`,
      `Inter 1st Year Marks: ${student.inter1Marks ?? '—'}`,
      `Inter 2nd Year Marks: ${student.inter2Marks ?? '—'}`,
      `Overall Percentage: ${student.overallPercentage ?? '—'}%`,
      `Mathematics: ${student.mathMarks ?? '—'} | Physics: ${student.physicsMarks ?? '—'} | Chemistry: ${student.chemMarks ?? '—'}`,
      `Entrance Score: ${student.entranceScore ?? '—'}`,
      `Predicted GPA (demo heuristic): ${student.predictedGPA ?? '—'} / 10`,
      `Performance Category: ${student.performanceCategory || '—'}`,
      `Support Recommendation: ${student.supportNeeded || '—'}`,
      '',
      'Branch Recommendations:'
    ];
    (student.branchRecs || []).forEach((rec) => reportLines.push(`• ${rec.branch} (${rec.fitScore}): ${rec.reason}`));
    reportLines.push('', 'Scholarship Screening:');
    (student.scholarships || []).forEach((sc) => reportLines.push(`• ${sc.type}: ${sc.status} — ${sc.amount}. Criteria: ${sc.criteria}`));
    reportLines.push('', 'Note: Predictions and eligibility indicators are demo estimates and must be reviewed by authorized staff.');

    doc.setFont('helvetica', 'normal');
    doc.setFontSize(10);
    reportLines.forEach((line) => {
      const wrapped = doc.splitTextToSize(line, maxWidth);
      const requiredHeight = Math.max(5, wrapped.length * 5);
      if (y + requiredHeight > 282) {
        doc.addPage();
        y = 18;
      }
      if (line.startsWith('Branch Recommendations:') || line.startsWith('Scholarship Screening:')) {
        doc.setFont('helvetica', 'bold');
      } else {
        doc.setFont('helvetica', 'normal');
      }
      doc.text(wrapped, left, y);
      y += requiredHeight;
    });
    doc.save(`${student.id || 'student'}_report.pdf`);
    showToast(`PDF report downloaded for ${student.name}.`);
  };

  const totalStudents = students.length;
  const highPerfCount = students.filter(s => s.performanceCategory === 'High').length;
  const modPerfCount = students.filter(s => s.performanceCategory === 'Moderate').length;
  const supportCount = students.filter(s => s.performanceCategory === 'Needs Support').length;
  const scholarshipEligibleCount = students.filter(s => s.scholarships.some(sc => sc.status === 'Eligible')).length;

  const branchDistributionData = students.reduce((acc, curr) => {
    const found = acc.find(item => item.name === curr.preferredBranch);
    if (found) found.count += 1;
    else acc.push({ name: curr.preferredBranch || 'General', count: 1 });
    return acc;
  }, []);

  const performancePieData = [
    { name: 'High Performance', value: highPerfCount, color: '#10B981' },
    { name: 'Moderate Performance', value: modPerfCount, color: '#F59E0B' },
    { name: 'Needs Support', value: supportCount, color: '#EF4444' },
  ];

  const filteredStudents = students.filter(s => {
    const matchesSearch = s.name.toLowerCase().includes(searchTerm.toLowerCase()) || s.id.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesCategory = categoryFilter === 'All' || s.performanceCategory === categoryFilter;
    return matchesSearch && matchesCategory;
  });

  const totalPages = Math.ceil(filteredStudents.length / rowsPerPage);
  const paginatedStudents = filteredStudents.slice((currentPage - 1) * rowsPerPage, currentPage * rowsPerPage);

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 font-sans flex flex-col selection:bg-cyan-500 selection:text-white">
      {toast && (
        <div className={`fixed top-6 right-6 z-50 px-6 py-3.5 rounded-2xl shadow-2xl text-white font-semibold flex items-center gap-3 transition-all backdrop-blur-md ${toast.type === 'error' ? 'bg-rose-600/90 border border-rose-400/30' : 'bg-emerald-600/90 border border-emerald-400/30'}`}>
          <span>{toast.message}</span>
        </div>
      )}

      {/* Top Header */}
      <header className="bg-slate-900/80 backdrop-blur-xl text-white sticky top-0 z-40 border-b border-slate-800/80 shadow-2xl">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-20 flex items-center justify-between">
          <div className="flex items-center space-x-3.5 cursor-pointer group" onClick={() => setCurrentView(currentUser ? 'dashboard' : 'login')}>
            <div className="w-12 h-12 rounded-2xl bg-gradient-to-tr from-cyan-600 via-blue-600 to-indigo-600 flex items-center justify-center shadow-lg shadow-cyan-500/30 ring-2 ring-cyan-400/30 group-hover:scale-105 transition-transform">
              <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"/>
              </svg>
            </div>
            <div>
              <h1 className="text-xl font-black tracking-wider bg-gradient-to-r from-white via-cyan-200 to-blue-300 bg-clip-text text-transparent">EduPredict AI</h1>
              <p className="text-xs text-cyan-400 font-medium tracking-wide">{settings.universityName}</p>
            </div>
          </div>

          {currentUser ? (
            <div className="flex items-center space-x-5">
              <div className="hidden md:block text-right">
                <p className="text-sm font-bold text-slate-100">{currentUser.name}</p>
                <span className="inline-block px-3 py-0.5 text-[11px] font-bold bg-cyan-500/20 text-cyan-300 rounded-full border border-cyan-500/30 mt-0.5">
                  {currentUser.role}
                </span>
              </div>
              <button 
                onClick={() => { setCurrentUser(null); setCurrentView('login'); showToast('Logged out successfully'); }}
                className="px-4 py-2 text-sm font-bold text-slate-300 hover:text-white bg-slate-800 hover:bg-slate-700 rounded-xl transition border border-slate-700 shadow-sm">
                Logout
              </button>
            </div>
          ) : (
            <div className="px-4 py-2 bg-slate-900/80 rounded-2xl border border-slate-800 shadow-inner text-xs font-bold tracking-wider text-cyan-300">
              Created by: David Sudheer
            </div>
          )}
        </div>
      </header>

      {/* Main Body */}
      <div className="flex-1 flex flex-col md:flex-row">
        {currentUser && (
          <aside className="w-full md:w-64 bg-slate-900/90 backdrop-blur-md text-slate-300 flex md:flex-col border-r border-slate-800/80 p-4 space-y-2 overflow-x-auto shadow-xl">
            <div className="text-[11px] font-extrabold text-slate-500 uppercase tracking-widest mb-2 px-3 hidden md:block">Navigation</div>
            <button 
              onClick={() => setCurrentView('dashboard')}
              className={`w-full flex items-center space-x-3 px-4 py-3 rounded-xl font-bold text-sm transition shadow-sm ${currentView === 'dashboard' ? 'bg-gradient-to-r from-cyan-600 to-blue-600 text-white shadow-cyan-600/30 ring-1 ring-cyan-400/30' : 'hover:bg-slate-800/80 text-slate-400 hover:text-slate-200'}`}>
              <span>Dashboard</span>
            </button>
            <button 
              onClick={() => setCurrentView('register')}
              className={`w-full flex items-center space-x-3 px-4 py-3 rounded-xl font-bold text-sm transition shadow-sm ${currentView === 'register' ? 'bg-gradient-to-r from-cyan-600 to-blue-600 text-white shadow-cyan-600/30 ring-1 ring-cyan-400/30' : 'hover:bg-slate-800/80 text-slate-400 hover:text-slate-200'}`}>
              <span>Student Registration</span>
            </button>
            <button 
              onClick={() => setCurrentView('students')}
              className={`w-full flex items-center space-x-3 px-4 py-3 rounded-xl font-bold text-sm transition shadow-sm ${currentView === 'students' ? 'bg-gradient-to-r from-cyan-600 to-blue-600 text-white shadow-cyan-600/30 ring-1 ring-cyan-400/30' : 'hover:bg-slate-800/80 text-slate-400 hover:text-slate-200'}`}>
              <span>Student Records</span>
            </button>
            <button 
              onClick={() => setCurrentView('datasets')}
              className={`w-full flex items-center space-x-3 px-4 py-3 rounded-xl font-bold text-sm transition shadow-sm ${currentView === 'datasets' ? 'bg-gradient-to-r from-cyan-600 to-blue-600 text-white shadow-cyan-600/30 ring-1 ring-cyan-400/30' : 'hover:bg-slate-800/80 text-slate-400 hover:text-slate-200'}`}>
              <span>Historical Datasets &amp; ML</span>
            </button>
            <button 
              onClick={() => setCurrentView('scholarships')}
              className={`w-full flex items-center space-x-3 px-4 py-3 rounded-xl font-bold text-sm transition shadow-sm ${currentView === 'scholarships' ? 'bg-gradient-to-r from-cyan-600 to-blue-600 text-white shadow-cyan-600/30 ring-1 ring-cyan-400/30' : 'hover:bg-slate-800/80 text-slate-400 hover:text-slate-200'}`}>
              <span>Scholarships</span>
            </button>

            {currentUser.role === 'Admin' && (
              <>
                <button 
                  onClick={() => setCurrentView('staff-management')}
                  className={`w-full flex items-center space-x-3 px-4 py-3 rounded-xl font-bold text-sm transition shadow-sm ${currentView === 'staff-management' ? 'bg-gradient-to-r from-cyan-600 to-blue-600 text-white shadow-cyan-600/30 ring-1 ring-cyan-400/30' : 'hover:bg-slate-800/80 text-slate-400 hover:text-slate-200'}`}>
                  <span>Staff Logins</span>
                </button>
                <button 
                  onClick={() => setCurrentView('settings')}
                  className={`w-full flex items-center space-x-3 px-4 py-3 rounded-xl font-bold text-sm transition shadow-sm ${currentView === 'settings' ? 'bg-gradient-to-r from-cyan-600 to-blue-600 text-white shadow-cyan-600/30 ring-1 ring-cyan-400/30' : 'hover:bg-slate-800/80 text-slate-400 hover:text-slate-200'}`}>
                  <span>Settings</span>
                </button>
              </>
            )}
          </aside>
        )}

        <main className="flex-1 p-6 md:p-10 bg-slate-950 overflow-y-auto">
          {currentView === 'login' && (
            <div className="max-w-md mx-auto mt-12 bg-slate-900/90 backdrop-blur-xl p-8 rounded-3xl shadow-2xl border border-slate-800">
              <div className="text-center mb-6">
                <div className="w-16 h-16 bg-gradient-to-tr from-cyan-600 via-blue-600 to-indigo-600 rounded-2xl mx-auto flex items-center justify-center shadow-lg shadow-cyan-500/20 mb-4 ring-2 ring-cyan-400/30">
                  <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"/></svg>
                </div>
                <h2 className="text-2xl font-black text-white">EduPredict AI Portal</h2>
                <p className="text-sm text-slate-400 mt-1">
                  {authMode === 'signin' ? 'Sign in to access university dashboard' : 'Create new staff or counselor account'}
                </p>
              </div>

              {/* Toggle Sign In / Sign Up */}
              <div className="flex bg-slate-950 p-1.5 rounded-2xl mb-6 border border-slate-800">
                <button
                  type="button"
                  onClick={() => setAuthMode('signin')}
                  className={`flex-1 py-2 text-xs font-bold rounded-xl transition ${authMode === 'signin' ? 'bg-cyan-600 text-white shadow-lg shadow-cyan-600/30' : 'text-slate-400 hover:text-white'}`}>
                  Sign In
                </button>
                <button
                  type="button"
                  onClick={() => setAuthMode('signup')}
                  className={`flex-1 py-2 text-xs font-bold rounded-xl transition ${authMode === 'signup' ? 'bg-cyan-600 text-white shadow-lg shadow-cyan-600/30' : 'text-slate-400 hover:text-white'}`}>
                  Sign Up (New Staff)
                </button>
              </div>

              {authMode === 'signin' ? (
                <>
                  {/* Quick Demo Credentials Box */}
                  <div className="mb-6 p-4 bg-slate-950/80 border border-slate-800 rounded-2xl shadow-inner">
                    <p className="text-[11px] font-black text-cyan-400 uppercase tracking-widest mb-1">Credentials: </p>
                    <p className="text-xs text-slate-400 mb-3">Click any one of these:</p>
                    <div className="flex gap-2">
                      <button 
                        type="button" 
                        onClick={() => {
                          setSelectedRoleType('Admin');
                          setLoginEmail('admin@edupredict.edu');
                          setLoginPassword('Admin@2026');
                        }}
                        className={`flex-1 py-2 text-xs font-bold rounded-xl transition shadow-md ${selectedRoleType === 'Admin' ? 'bg-gradient-to-r from-cyan-600 to-blue-600 text-white shadow-cyan-600/30 ring-1 ring-cyan-400/30' : 'bg-slate-900 text-slate-300 border border-slate-800 hover:bg-slate-800'}`}>
                        Admin
                      </button>
                      <button 
                        type="button" 
                        onClick={() => {
                          setSelectedRoleType('Staff');
                          setLoginEmail('staff@edupredict.edu');
                          setLoginPassword('Staff@2026');
                        }}
                        className={`flex-1 py-2 text-xs font-bold rounded-xl transition shadow-md ${selectedRoleType === 'Staff' ? 'bg-gradient-to-r from-cyan-600 to-blue-600 text-white shadow-cyan-600/30 ring-1 ring-cyan-400/30' : 'bg-slate-900 text-slate-300 border border-slate-800 hover:bg-slate-800'}`}>
                        Staff
                      </button>
                      <button 
                        type="button" 
                        onClick={() => {
                          setSelectedRoleType('Counselor');
                          setLoginEmail('counselor@edupredict.edu');
                          setLoginPassword('Counselor@2026');
                        }}
                        className={`flex-1 py-2 text-xs font-bold rounded-xl transition shadow-md ${selectedRoleType === 'Counselor' ? 'bg-gradient-to-r from-cyan-600 to-blue-600 text-white shadow-cyan-600/30 ring-1 ring-cyan-400/30' : 'bg-slate-900 text-slate-300 border border-slate-800 hover:bg-slate-800'}`}>
                        Counselor
                      </button>
                    </div>
                  </div>

                  <form onSubmit={handleLogin} className="space-y-4">
                    <div>
                      <label className="block text-xs font-bold text-slate-300 uppercase tracking-wider mb-2">University Email</label>
                      <input 
                        type="email" 
                        required 
                        value={loginEmail}
                        onChange={(e) => setLoginEmail(e.target.value)}
                        className="w-full px-4 py-3 rounded-xl bg-slate-950 border border-slate-800 text-white placeholder-slate-600 focus:ring-2 focus:ring-cyan-600 focus:outline-none"
                      />
                    </div>

                    <div>
                      <label className="block text-xs font-bold text-slate-300 uppercase tracking-wider mb-2">Password</label>
                      <input 
                        type="password" 
                        required 
                        value={loginPassword}
                        onChange={(e) => setLoginPassword(e.target.value)}
                        className="w-full px-4 py-3 rounded-xl bg-slate-950 border border-slate-800 text-white placeholder-slate-600 focus:ring-2 focus:ring-cyan-600 focus:outline-none"
                      />
                    </div>

                    <button 
                      type="submit"
                      className="w-full py-3.5 bg-gradient-to-r from-cyan-600 via-blue-600 to-indigo-600 hover:from-cyan-500 hover:to-indigo-500 text-white font-bold rounded-xl shadow-lg shadow-cyan-600/30 transition mt-2">
                      Secure Sign In
                    </button>
                  </form>
                </>
              ) : (
                <form onSubmit={handleSignup} className="space-y-4">
                  <div>
                    <label className="block text-xs font-bold text-slate-300 uppercase tracking-wider mb-1">Full Name</label>
                    <input 
                      type="text" 
                      required 
                      placeholder="e.g. Dr. Rajesh Kumar"
                      value={signupForm.name}
                      onChange={(e) => setSignupForm({...signupForm, name: e.target.value})}
                      className="w-full px-4 py-2.5 rounded-xl bg-slate-950 border border-slate-800 text-white focus:ring-2 focus:ring-cyan-600 focus:outline-none"
                    />
                  </div>

                  <div>
                    <label className="block text-xs font-bold text-slate-300 uppercase tracking-wider mb-1">University Email</label>
                    <input 
                      type="email" 
                      required 
                      placeholder="e.g. rajesh@edupredict.edu"
                      value={signupForm.email}
                      onChange={(e) => setSignupForm({...signupForm, email: e.target.value})}
                      className="w-full px-4 py-2.5 rounded-xl bg-slate-950 border border-slate-800 text-white focus:ring-2 focus:ring-cyan-600 focus:outline-none"
                    />
                  </div>

                  <div>
                    <label className="block text-xs font-bold text-slate-300 uppercase tracking-wider mb-1">Assigned Role</label>
                    <select
                      value={signupForm.role}
                      onChange={(e) => setSignupForm({...signupForm, role: e.target.value})}
                      className="w-full px-4 py-2.5 rounded-xl bg-slate-950 border border-slate-800 text-white focus:ring-2 focus:ring-cyan-600 focus:outline-none">
                      <option value="Admission Staff">Admission Staff</option>
                      <option value="Academic Counselor">Academic Counselor</option>
                      <option value="Admin">Administrator</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-xs font-bold text-slate-300 uppercase tracking-wider mb-1">Password</label>
                    <input 
                      type="password" 
                      required 
                      placeholder="••••••••"
                      value={signupForm.password}
                      onChange={(e) => setSignupForm({...signupForm, password: e.target.value})}
                      className="w-full px-4 py-2.5 rounded-xl bg-slate-950 border border-slate-800 text-white focus:ring-2 focus:ring-cyan-600 focus:outline-none"
                    />
                  </div>

                  <div>
                    <label className="block text-xs font-bold text-slate-300 uppercase tracking-wider mb-1">Confirm Password</label>
                    <input 
                      type="password" 
                      required 
                      placeholder="••••••••"
                      value={signupForm.confirmPassword}
                      onChange={(e) => setSignupForm({...signupForm, confirmPassword: e.target.value})}
                      className="w-full px-4 py-2.5 rounded-xl bg-slate-950 border border-slate-800 text-white focus:ring-2 focus:ring-cyan-600 focus:outline-none"
                    />
                  </div>

                  <button 
                    type="submit"
                    className="w-full py-3.5 bg-gradient-to-r from-cyan-600 via-blue-600 to-indigo-600 hover:from-cyan-500 hover:to-indigo-500 text-white font-bold rounded-xl shadow-lg shadow-cyan-600/30 transition mt-2">
                    Create Account &amp; Sign In
                  </button>
                </form>
              )}
            </div>
          )}

          {currentView === 'dashboard' && currentUser && (
            <div className="space-y-8">
              <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div>
                  <h2 className="text-3xl font-black text-white tracking-tight">University Dashboard</h2>
                  <p className="text-slate-400 text-sm mt-1">Overview of student admissions, AI performance predictions, and analytics.</p>
                </div>
                <button 
                  onClick={() => setCurrentView('register')}
                  className="px-6 py-3 bg-gradient-to-r from-cyan-600 via-blue-600 to-indigo-600 hover:from-cyan-500 hover:to-indigo-500 text-white font-bold rounded-2xl shadow-xl shadow-cyan-600/30 transition">
                  + New Student Registration
                </button>
              </div>

              {/* KPI Cards */}
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
                <div className="bg-slate-900/80 backdrop-blur-xl p-6 rounded-3xl shadow-xl border border-slate-800/80 hover:border-cyan-500/50 transition-all group">
                  <p className="text-xs font-bold text-slate-400 uppercase tracking-wider">Total Registered</p>
                  <h3 className="text-4xl font-black text-white mt-2 group-hover:scale-105 transition-transform">{totalStudents}</h3>
                </div>
                <div className="bg-slate-900/80 backdrop-blur-xl p-6 rounded-3xl shadow-xl border border-slate-800/80 hover:border-emerald-500/50 transition-all group">
                  <p className="text-xs font-bold text-slate-400 uppercase tracking-wider">High Performers</p>
                  <h3 className="text-4xl font-black text-emerald-400 mt-2 group-hover:scale-105 transition-transform">{highPerfCount}</h3>
                </div>
                <div className="bg-slate-900/80 backdrop-blur-xl p-6 rounded-3xl shadow-xl border border-slate-800/80 hover:border-rose-500/50 transition-all group">
                  <p className="text-xs font-bold text-slate-400 uppercase tracking-wider">Needs Support</p>
                  <h3 className="text-4xl font-black text-rose-400 mt-2 group-hover:scale-105 transition-transform">{supportCount}</h3>
                </div>
                <div className="bg-slate-900/80 backdrop-blur-xl p-6 rounded-3xl shadow-xl border border-slate-800/80 hover:border-indigo-500/50 transition-all group">
                  <p className="text-xs font-bold text-slate-400 uppercase tracking-wider">Scholarship Eligible</p>
                  <h3 className="text-4xl font-black text-indigo-400 mt-2 group-hover:scale-105 transition-transform">{scholarshipEligibleCount}</h3>
                </div>
              </div>

              <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                <div className="bg-slate-900/80 backdrop-blur-xl p-6 rounded-3xl shadow-xl border border-slate-800/80">
                  <h3 className="text-lg font-extrabold text-white mb-4">Performance Category Distribution</h3>
                  <div className="h-72">
                    <ResponsiveContainer width="100%" height="100%">
                      <PieChart>
                        <Pie data={performancePieData} cx="50%" cy="50%" innerRadius={70} outerRadius={100} dataKey="value" label>
                          {performancePieData.map((entry, index) => (
                            <Cell key={`cell-${index}`} fill={entry.color} />
                          ))}
                        </Pie>
                        <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '1rem', color: '#fff' }} />
                        <Legend />
                      </PieChart>
                    </ResponsiveContainer>
                  </div>
                </div>

                <div className="bg-slate-900/80 backdrop-blur-xl p-6 rounded-3xl shadow-xl border border-slate-800/80">
                  <h3 className="text-lg font-extrabold text-white mb-4">Preferred Branch Distribution</h3>
                  <div className="h-72">
                    <ResponsiveContainer width="100%" height="100%">
                      <BarChart data={branchDistributionData}>
                        <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#334155" />
                        <XAxis dataKey="name" tick={{ fontSize: 11, fill: '#94a3b8' }} />
                        <YAxis tick={{ fill: '#94a3b8' }} />
                        <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '1rem', color: '#fff' }} />
                        <Bar dataKey="count" fill="#06b6d4" radius={[10, 10, 0, 0]} />
                      </BarChart>
                    </ResponsiveContainer>
                  </div>
                </div>
              </div>
            </div>
          )}

          {currentView === 'register' && currentUser && (
            <div className="max-w-4xl mx-auto bg-slate-900/80 backdrop-blur-xl p-8 rounded-3xl shadow-2xl border border-slate-800">
              <h2 className="text-2xl font-black text-white mb-6">Student Registration &amp; ML Evaluation</h2>
              <form onSubmit={handleRegisterSubmit} className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <label className="block text-xs font-bold text-slate-300 uppercase tracking-wider mb-2">Student Full Name *</label>
                    <input 
                      type="text" 
                      placeholder="e.g. Priya Nair"
                      value={regForm.name}
                      onChange={e => setRegForm({...regForm, name: e.target.value})}
                      className={`w-full px-4 py-3 rounded-xl bg-slate-950 border text-white ${formErrors.name ? 'border-rose-500 bg-rose-950/20' : 'border-slate-800'}`}
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-bold text-slate-300 uppercase tracking-wider mb-2">Student ID *</label>
                    <input 
                      type="text" 
                      value={regForm.id}
                      onChange={e => setRegForm({...regForm, id: e.target.value})}
                      className="w-full px-4 py-3 rounded-xl bg-slate-950 border border-slate-800 text-slate-400"
                    />
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  <div>
                    <label className="block text-xs font-bold text-slate-300 uppercase tracking-wider mb-2">Inter 1st Year Marks *</label>
                    <input 
                      type="number" 
                      placeholder="e.g. 456"
                      value={regForm.inter1Marks}
                      onChange={e => setRegForm({...regForm, inter1Marks: e.target.value})}
                      className="w-full px-4 py-3 rounded-xl bg-slate-950 border border-slate-800 text-white"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-bold text-slate-300 uppercase tracking-wider mb-2">Inter 2nd Year Marks *</label>
                    <input 
                      type="number" 
                      placeholder="e.g. 540"
                      value={regForm.inter2Marks}
                      onChange={e => setRegForm({...regForm, inter2Marks: e.target.value})}
                      className="w-full px-4 py-3 rounded-xl bg-slate-950 border border-slate-800 text-white"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-bold text-slate-300 uppercase tracking-wider mb-2">Overall Percentage (%)</label>
                    <input 
                      type="number" 
                      step="0.1"
                      placeholder="e.g. 90.0"
                      value={regForm.overallPercentage}
                      onChange={e => setRegForm({...regForm, overallPercentage: e.target.value})}
                      className="w-full px-4 py-3 rounded-xl bg-slate-950 border border-slate-800 text-white"
                    />
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  <div>
                    <label className="block text-xs font-bold text-slate-300 uppercase tracking-wider mb-2">Math Marks (out of 100)</label>
                    <input 
                      type="number" 
                      placeholder="e.g. 92"
                      value={regForm.mathMarks}
                      onChange={e => setRegForm({...regForm, mathMarks: e.target.value})}
                      className="w-full px-4 py-3 rounded-xl bg-slate-950 border border-slate-800 text-white"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-bold text-slate-300 uppercase tracking-wider mb-2">Physics Marks (out of 100)</label>
                    <input 
                      type="number" 
                      placeholder="e.g. 88"
                      value={regForm.physicsMarks}
                      onChange={e => setRegForm({...regForm, physicsMarks: e.target.value})}
                      className="w-full px-4 py-3 rounded-xl bg-slate-950 border border-slate-800 text-white"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-bold text-slate-300 uppercase tracking-wider mb-2">Chemistry Marks (out of 100)</label>
                    <input 
                      type="number" 
                      placeholder="e.g. 85"
                      value={regForm.chemMarks}
                      onChange={e => setRegForm({...regForm, chemMarks: e.target.value})}
                      className="w-full px-4 py-3 rounded-xl bg-slate-950 border border-slate-800 text-white"
                    />
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  <div>
                    <label className="block text-xs font-bold text-slate-300 uppercase tracking-wider mb-2">Preferred Degree &amp; Branch</label>
                    <select 
                      value={regForm.preferredBranch}
                      onChange={e => setRegForm({...regForm, preferredBranch: e.target.value})}
                      className="w-full px-4 py-3 rounded-xl bg-slate-950 border border-slate-800 text-white">
                      <option value="Computer Science & Engineering">Computer Science &amp; Engineering</option>
                      <option value="Artificial Intelligence & Data Science">Artificial Intelligence & Data Science</option>
                      <option value="Electronics & Communication">Electronics &amp; Communication</option>
                      <option value="Mechanical Engineering">Mechanical Engineering</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-xs font-bold text-slate-300 uppercase tracking-wider mb-2">Entrance Exam Score</label>
                    <input 
                      type="number" 
                      placeholder="e.g. 800"
                      value={regForm.entranceScore}
                      onChange={e => setRegForm({...regForm, entranceScore: e.target.value})}
                      className="w-full px-4 py-3 rounded-xl bg-slate-950 border border-slate-800 text-white"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-bold text-slate-300 uppercase tracking-wider mb-2">Annual Household Income (₹)</label>
                    <input 
                      type="number" 
                      placeholder="e.g. 400000"
                      value={regForm.householdIncome}
                      onChange={e => setRegForm({...regForm, householdIncome: e.target.value})}
                      className="w-full px-4 py-3 rounded-xl bg-slate-950 border border-slate-800 text-white"
                    />
                  </div>
                </div>

                <div className="flex justify-end pt-4">
                  <button 
                    type="submit"
                    className="px-8 py-3.5 bg-gradient-to-r from-cyan-600 via-blue-600 to-indigo-600 hover:from-cyan-500 hover:to-indigo-500 text-white font-bold rounded-2xl shadow-xl shadow-cyan-600/30 transition">
                    Submit
                  </button>
                </div>
              </form>
            </div>
          )}

          {currentView === 'students' && currentUser && (
            <div className="space-y-6">
              <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                <h2 className="text-3xl font-black text-white">Student Records &amp; AI Profiles</h2>
                <input 
                  type="text" 
                  placeholder="Search student..."
                  value={searchTerm}
                  onChange={e => setSearchTerm(e.target.value)}
                  className="px-4 py-2.5 rounded-xl bg-slate-900 border border-slate-800 text-white text-sm w-64 focus:ring-2 focus:ring-cyan-600 focus:outline-none"
                />
              </div>
              <div className="bg-slate-900/80 backdrop-blur-xl rounded-3xl shadow-xl border border-slate-800 overflow-hidden">
                <table className="w-full text-left border-collapse">
                  <thead>
                    <tr className="bg-slate-950 border-b border-slate-800 text-xs font-bold text-slate-400 uppercase tracking-wider">
                      <th className="p-4">ID</th>
                      <th className="p-4">Name</th>
                      <th className="p-4">Branch</th>
                      <th className="p-4">Predicted GPA</th>
                      <th className="p-4">Category</th>
                      <th className="p-4 text-right">Action</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800 text-sm">
                    {paginatedStudents.map((st, idx) => (
                      <tr key={idx} className="hover:bg-slate-800/50">
                        <td className="p-4 font-bold text-cyan-400">{st.id}</td>
                        <td className="p-4 font-semibold text-white">{st.name}</td>
                        <td className="p-4 text-slate-300">{st.preferredBranch}</td>
                        <td className="p-4 font-extrabold text-white">{st.predictedGPA} / 10</td>
                        <td className="p-4"><span className="px-3 py-1 text-xs font-bold rounded-full bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">{st.performanceCategory}</span></td>
                        <td className="p-4 text-right">
                          <button onClick={() => { setSelectedStudent(st); setCurrentView('report'); }} className="px-3 py-1.5 bg-cyan-600/20 hover:bg-cyan-600/30 text-cyan-300 rounded-xl text-xs font-bold border border-cyan-500/30 transition">View Report</button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {currentView === 'datasets' && currentUser && (
            <div className="space-y-6">
              <div className="flex justify-between items-center">
                <h2 className="text-3xl font-black text-white">Historical Datasets &amp; ML Pipelines</h2>
                {currentUser.role === 'Admin' && (
                  <label className="cursor-pointer px-6 py-3 bg-gradient-to-r from-cyan-600 to-blue-600 text-white font-bold rounded-2xl shadow-xl shadow-cyan-600/30 inline-flex items-center gap-2 hover:scale-105 transition-transform">
                    <span>Upload CSV &amp; Retrain</span>
                    <input type="file" accept=".csv" onChange={handleRealCSVUpload} className="hidden" />
                  </label>
                )}
              </div>
              <div className="bg-slate-900/80 backdrop-blur-xl rounded-3xl shadow-xl border border-slate-800 overflow-hidden">
                <table className="w-full text-left">
                  <thead>
                    <tr className="bg-slate-950 border-b border-slate-800 text-xs font-bold text-slate-400 uppercase tracking-wider">
                      <th className="p-4">File Name</th>
                      <th className="p-4">Records</th>
                      <th className="p-4">Status</th>
                      <th className="p-4 text-right">Action</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800 text-sm">
                    {historicalDatasets.map((ds, idx) => (
                      <tr key={idx} className="hover:bg-slate-800/50">
                        <td className="p-4 font-bold text-white">{ds.fileName}</td>
                        <td className="p-4 text-slate-300">{ds.recordsCount} rows</td>
                        <td className="p-4"><span className="px-3 py-1 text-xs font-bold rounded-full bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">{ds.status}</span></td>
                        <td className="p-4 text-right">
                          <button onClick={() => setActiveDatasetView(ds)} className="px-3 py-1.5 bg-cyan-600/20 hover:bg-cyan-600/30 text-cyan-300 rounded-xl text-xs font-bold border border-cyan-500/30 transition">View Dataset</button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              {activeDatasetView && (
                <div className="fixed inset-0 z-50 bg-slate-950/80 backdrop-blur-md flex items-center justify-center p-4">
                  <div className="bg-slate-900 w-full max-w-2xl rounded-3xl shadow-2xl p-6 space-y-4 border border-slate-800">
                    <div className="flex justify-between items-center border-b border-slate-800 pb-4">
                      <h3 className="font-bold text-lg text-white">Dataset View: {activeDatasetView.fileName}</h3>
                      <button onClick={() => setActiveDatasetView(null)} className="font-bold text-slate-400 hover:text-white">✕</button>
                    </div>
                    <table className="w-full text-left text-xs text-slate-300">
                      <thead className="bg-slate-950 text-slate-400 font-bold uppercase tracking-wider">
                        <tr>
                          <th className="p-3">ID</th>
                          <th className="p-3">Name</th>
                          <th className="p-3">Math</th>
                          <th className="p-3">GPA</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-800">
                        {activeDatasetView.sampleRows.map((r, rIdx) => (
                          <tr key={rIdx} className="hover:bg-slate-800/50">
                            <td className="p-3 font-semibold text-cyan-400">{r.id}</td>
                            <td className="p-3 font-semibold text-white">{r.name}</td>
                            <td className="p-3">{r.math}</td>
                            <td className="p-3 font-bold text-emerald-400">{r.gpa}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}
            </div>
          )}

          {currentView === 'scholarships' && currentUser && (
            <div className="space-y-6">
              <h2 className="text-3xl font-black text-white">Scholarship Eligibility Audit</h2>
              <div className="bg-slate-900/80 backdrop-blur-xl rounded-3xl shadow-xl border border-slate-800 overflow-hidden">
                <table className="w-full text-left">
                  <thead>
                    <tr className="bg-slate-950 border-b border-slate-800 text-xs font-bold text-slate-400 uppercase tracking-wider">
                      <th className="p-4">Student</th>
                      <th className="p-4">Merit Status</th>
                      <th className="p-4">Need Status</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800 text-sm">
                    {students.map((st, idx) => (
                      <tr key={idx} className="hover:bg-slate-800/50">
                        <td className="p-4 font-bold text-white">{st.name}</td>
                        <td className="p-4"><span className="px-3 py-1 text-xs font-bold rounded-full bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">{st.scholarships[0]?.status}</span></td>
                        <td className="p-4"><span className="px-3 py-1 text-xs font-bold rounded-full bg-slate-800 text-slate-300 border border-slate-700">{st.scholarships[1]?.status}</span></td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {currentView === 'staff-management' && currentUser && currentUser.role === 'Admin' && (
            <div className="max-w-3xl mx-auto bg-slate-900/80 backdrop-blur-xl p-8 rounded-3xl shadow-2xl border border-slate-800 space-y-6">
              <h2 className="text-2xl font-black text-white">Staff &amp; Counselor Credential Management</h2>
              <form onSubmit={(e) => {
                e.preventDefault();
                if (!newStaffForm.name || !newStaffForm.email || !newStaffForm.password) return;
                setRegisteredUsers([...registeredUsers, newStaffForm]);
                showToast(`Created credential for ${newStaffForm.name}!`);
                setNewStaffForm({ name: '', email: '', role: 'Admission Staff', password: '' });
              }} className="space-y-4 bg-slate-950 p-6 rounded-2xl border border-slate-800">
                <h3 className="font-bold text-sm text-white">Add New Staff</h3>
                <input type="text" placeholder="Name" value={newStaffForm.name} onChange={e => setNewStaffForm({...newStaffForm, name: e.target.value})} className="w-full px-4 py-2.5 rounded-xl bg-slate-900 border border-slate-800 text-white text-sm" />
                <input type="email" placeholder="Email" value={newStaffForm.email} onChange={e => setNewStaffForm({...newStaffForm, email: e.target.value})} className="w-full px-4 py-2.5 rounded-xl bg-slate-900 border border-slate-800 text-white text-sm" />
                <input type="password" placeholder="Password" value={newStaffForm.password} onChange={e => setNewStaffForm({...newStaffForm, password: e.target.value})} className="w-full px-4 py-2.5 rounded-xl bg-slate-900 border border-slate-800 text-white text-sm" />
                <button type="submit" className="px-5 py-2.5 bg-gradient-to-r from-cyan-600 to-blue-600 text-white rounded-xl text-xs font-bold shadow-md">Add Staff</button>
              </form>
            </div>
          )}

          {currentView === 'settings' && currentUser && currentUser.role === 'Admin' && (
            <div className="max-w-2xl mx-auto bg-slate-900/80 backdrop-blur-xl p-8 rounded-3xl shadow-2xl border border-slate-800 space-y-6">
              <h2 className="text-2xl font-black text-white">Portal Settings</h2>
              <div>
                <label className="block text-xs font-bold text-slate-300 uppercase tracking-wider mb-2">University Name</label>
                <input type="text" value={settings.universityName} onChange={e => setSettings({...settings, universityName: e.target.value})} className="w-full px-4 py-3 rounded-xl bg-slate-950 border border-slate-800 text-white text-sm" />
              </div>
              <button onClick={() => showToast('Settings updated successfully!')} className="px-6 py-3 bg-gradient-to-r from-cyan-600 to-blue-600 text-white rounded-xl font-bold text-sm shadow-lg">Save Changes</button>
            </div>
          )}

          {currentView === 'report' && selectedStudent && currentUser && (
            <div className="max-w-4xl mx-auto bg-slate-900/80 backdrop-blur-xl p-8 rounded-3xl shadow-2xl border border-slate-800 space-y-8">
              <div className="flex justify-between items-center border-b border-slate-800 pb-4">
                <div>
                  <h2 className="text-3xl font-black text-white">{selectedStudent.name}</h2>
                  <p className="text-xs text-cyan-400 font-bold">Student ID: {selectedStudent.id} | Preferred: {selectedStudent.preferredBranch}</p>
                </div>
                <div className="flex gap-3">
                  <button 
                    onClick={() => exportStudentPdf(selectedStudent)} 
                    className="px-4 py-2 bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 text-white text-xs font-bold rounded-xl shadow-lg transition">
                    Download PDF Report
                  </button>
                  <button 
                    onClick={() => exportStudentCsv(selectedStudent)} 
                    className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-white text-xs font-bold rounded-xl border border-slate-700 transition">
                    Export CSV
                  </button>
                  <button onClick={() => setCurrentView('students')} className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-white text-xs font-bold rounded-xl transition">Back</button>
                </div>
              </div>

              {/* Prediction & GPA Summary Cards */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="bg-slate-950 p-6 rounded-2xl border border-slate-800">
                  <p className="text-xs text-slate-400 font-bold uppercase tracking-wider">Expected 1st-Year Academic Performance</p>
                  <div className="flex items-baseline gap-3 mt-2">
                    <h3 className="text-4xl font-black text-cyan-400">{selectedStudent.predictedGPA} <span className="text-sm font-normal text-slate-400">/ 10 GPA</span></h3>
                    <span className="px-3 py-1 text-xs font-bold rounded-full bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">{selectedStudent.performanceCategory}</span>
                  </div>
                </div>

                <div className="bg-slate-950 p-6 rounded-2xl border border-slate-800">
                  <p className="text-xs text-slate-400 font-bold uppercase tracking-wider">Academic Support Recommendation</p>
                  <p className="text-sm font-bold text-slate-200 mt-2">{selectedStudent.supportNeeded}</p>
                </div>
              </div>

              {/* Branch Recommendations */}
              <div className="bg-slate-950 p-6 rounded-2xl border border-slate-800 space-y-4">
                <h3 className="font-extrabold text-white text-lg">Intelligent Branch Recommendations</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {selectedStudent.branchRecs?.map((rec, rIdx) => (
                    <div key={rIdx} className="bg-slate-900 p-4 rounded-xl border border-slate-800">
                      <div className="flex justify-between items-center mb-1">
                        <span className="font-bold text-sm text-white">{rec.branch}</span>
                        <span className="px-2 py-0.5 text-xs font-extrabold bg-cyan-500/20 text-cyan-300 rounded-md">{rec.fitScore} Fit</span>
                      </div>
                      <p className="text-xs text-slate-400">{rec.reason}</p>
                    </div>
                  ))}
                </div>
              </div>

              {/* Scholarship Eligibility */}
              <div className="bg-slate-950 p-6 rounded-2xl border border-slate-800 space-y-4">
                <h3 className="font-extrabold text-white text-lg">Scholarship Eligibility Assessment</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {selectedStudent.scholarships?.map((sc, sIdx) => (
                    <div key={sIdx} className="bg-slate-900 p-4 rounded-xl border border-slate-800 flex justify-between items-center">
                      <div>
                        <p className="font-bold text-sm text-white">{sc.type}</p>
                        <p className="text-xs text-slate-400 mt-0.5">{sc.criteria}</p>
                      </div>
                      <span className={`px-3 py-1 text-xs font-bold rounded-full ${sc.status === 'Eligible' ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30' : 'bg-slate-800 text-slate-400 border border-slate-700'}`}>
                        {sc.status} ({sc.amount})
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}
        </main>
      </div>
    </div>
  );
}