# Terminology Alignment Fixes

## 🎯 **Priority 1: User-Facing Terminology Changes**

### **1. Intelligence Hub → Strategic Intelligence Center**

**Current**: "Intelligence Hub" (technical term)
**Target**: "Strategic Intelligence Center" (business term)

**Files to Update**:

- `apps/admin_web/src/ui/Dashboard.jsx` - Tab name
- `apps/admin_web/src/features/intelligence/IntelligenceHub.jsx` - Component name and title
- API documentation

**Implementation**:

```javascript
// Change from:
<h1 className="text-3xl font-bold">Intelligence Hub</h1>

// To:
<h1 className="text-3xl font-bold">Strategic Intelligence Center</h1>
```

### **2. Truths → Strategic Insights**

**Current**: "truths" (technical term)
**Target**: "Strategic Insights" (business term)

**Files to Update**:

- `apps/admin_web/src/features/intelligence/IntelligenceHub.jsx` - UI labels
- API endpoint documentation
- Dashboard labels

**Implementation**:

```javascript
// Change from:
<p className="text-sm font-medium text-muted-foreground">Total Truths</p>

// To:
<p className="text-sm font-medium text-muted-foreground">Strategic Insights</p>
```

### **3. Communications → Priority Communications**

**Current**: "communications" (generic term)
**Target**: "Priority Communications" (business term)

**Files to Update**:

- `apps/admin_web/src/features/intelligence/IntelligenceHub.jsx` - Tab and section names
- API endpoint names

**Implementation**:

```javascript
// Change from:
<TabsTrigger value="communications">Communications</TabsTrigger>

// To:
<TabsTrigger value="communications">Priority Communications</TabsTrigger>
```

### **4. Agent Results → Market Intelligence**

**Current**: "agent results" (technical term)
**Target**: "Market Intelligence" (business term)

**Files to Update**:

- Template descriptions
- UI labels
- API documentation

**Implementation**:

```javascript
// Change from:
"Transform agent data into organizational truths"

// To:
"Transform market intelligence into strategic insights"
```

## 🎯 **Priority 2: API Endpoint Naming**

### **Current API Structure**

```text
/intelligence/generate
/intelligence/truths
/intelligence/communications
/intelligence/templates
```

### **Proposed API Structure**

```text
/strategic-intelligence/generate
/strategic-intelligence/insights
/strategic-intelligence/communications
/strategic-intelligence/templates
```

## 🎯 **Priority 3: Component Naming**

### **File Renames**

- `IntelligenceHub.jsx` → `StrategicIntelligenceCenter.jsx`
- `intelligence_models.py` → `strategic_intelligence_models.py`
- `intelligence_service.py` → `strategic_intelligence_service.py`
- `intelligence.py` → `strategic_intelligence.py`

### **Class Renames**

- `IntelligenceService` → `StrategicIntelligenceService`
- `IntelligenceRequest` → `StrategicIntelligenceRequest`
- `IntelligenceResponse` → `StrategicIntelligenceResponse`

## 🎯 **Priority 4: Database/Model Field Names**

### **Keep Technical Names for Internal Use**

- `OrganizationalTruth` (internal model name)
- `CommunicationQueue` (internal model name)
- `agent_results` (internal field names)

### **Use Business Names for User Interface**

- "Strategic Insights" (user-facing)
- "Priority Communications" (user-facing)
- "Market Intelligence" (user-facing)

## 🔧 **Implementation Strategy**

### **Phase 1: User Interface Updates**

1. Update React component names and labels
2. Update tab names and navigation
3. Update dashboard labels and descriptions

### **Phase 2: API Documentation Updates**

1. Update API endpoint documentation
2. Update response field descriptions
3. Update example responses

### **Phase 3: Internal Refactoring**

1. Rename internal classes and methods
2. Update import statements
3. Update test files

### **Phase 4: Database Schema Updates**

1. Update field names in models
2. Update database migration scripts
3. Update query references

## 📋 **Specific File Changes**

### **High Priority (User-Facing)**

1. `apps/admin_web/src/ui/Dashboard.jsx`
2. `apps/admin_web/src/features/intelligence/IntelligenceHub.jsx`
3. API documentation files

### **Medium Priority (Internal)**

1. `apps/api/app/routers/intelligence.py`
2. `apps/api/app/domain/intelligence_service.py`
3. `apps/api/app/domain/intelligence_models.py`

### **Low Priority (Infrastructure)**

1. Database migration scripts
2. Test files
3. Configuration files

## 🎯 **Success Criteria**

### **User Experience**

- Users see business terminology, not technical terms
- Interface feels intuitive and professional
- Clear understanding of system purpose

### **Developer Experience**

- Internal code remains technically accurate
- Clear separation between internal and external naming
- Consistent naming conventions

### **Business Alignment**

- Terminology aligns with strategic management concepts
- Clear value proposition communication
- Professional appearance to stakeholders

## 🚀 **Next Steps**

1. **Review and approve terminology changes**
2. **Create implementation plan with phases**
3. **Start with user-facing changes**
4. **Test user experience impact**
5. **Gradually update internal components**

This alignment will ensure our system communicates its value proposition clearly while maintaining technical accuracy internally.
