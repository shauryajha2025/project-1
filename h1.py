import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date

# Set page configuration
st.set_page_config(
    page_title="Retirement Planner",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .sub-header {
        font-size: 1.8rem;
        color: #ff7f0e;
        margin-bottom: 1rem;
    }
    .highlight {
        background-color: #f0f2f6;
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 20px;
    }
    .result-box {
        background-color: #e6f3ff;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
    .positive {
        color: #2e8b57;
        font-weight: bold;
    }
    .warning {
        color: #ff4500;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# App title and description
st.markdown('<h1 class="main-header">💰 Retirement Planning Calculator</h1>', unsafe_allow_html=True)
st.write("Plan your retirement with this interactive calculator. Adjust the inputs in the sidebar to see how different factors affect your retirement savings.")

# Sidebar for user inputs
with st.sidebar:
    st.header("Personal Information")
    
    # User inputs
    current_age = st.slider("Current Age", 20, 70, 35)
    retirement_age = st.slider("Desired Retirement Age", 50, 80, 65)
    life_expectancy = st.slider("Life Expectancy", 75, 100, 85)
    
    st.header("Financial Information")
    
    current_savings = st.number_input("Current Retirement Savings ($)", min_value=0, value=50000, step=1000)
    annual_contribution = st.number_input("Annual Contribution ($)", min_value=0, value=10000, step=1000)
    annual_return = st.slider("Expected Annual Return (%)", 1.0, 15.0, 7.0, step=0.5)
    inflation_rate = st.slider("Expected Inflation Rate (%)", 0.5, 5.0, 2.5, step=0.1)
    
    st.header("Retirement Income")
    
    desired_income = st.number_input("Desired Annual Retirement Income (Today's $)", min_value=0, value=60000, step=5000)
    pension_income = st.number_input("Expected Annual Pension Income ($)", min_value=0, value=0, step=1000)
    social_security = st.number_input("Expected Annual Social Security ($)", min_value=0, value=15000, step=1000)
    
    # Calculate button
    calculate = st.button("Calculate Retirement Plan", type="primary")

# Main calculation function
def calculate_retirement(current_age, retirement_age, life_expectancy, current_savings, 
                         annual_contribution, annual_return, inflation_rate, desired_income, 
                         pension_income, social_security):
    
    # Calculate years until retirement and retirement duration
    years_to_retirement = retirement_age - current_age
    retirement_duration = life_expectancy - retirement_age
    
    # Initialize lists for results
    years = []
    ages = []
    savings = []
    contributions = []
    growth = []
    inflation_adjusted_savings = []
    retirement_income_needed = []
    
    # Calculate savings growth until retirement
    savings_balance = current_savings
    for year in range(years_to_retirement + 1):
        age = current_age + year
        years.append(year)
        ages.append(age)
        
        if year == 0:
            contributions.append(0)
            growth.append(0)
        else:
            # Calculate investment growth
            investment_growth = savings_balance * (annual_return / 100)
            growth.append(investment_growth)
            
            # Add contribution at the beginning of the year
            savings_balance += annual_contribution
            contributions.append(annual_contribution)
            
            # Add investment growth
            savings_balance += investment_growth
        
        savings.append(savings_balance)
        
        # Calculate inflation-adjusted savings
        inflation_adjusted = savings_balance / ((1 + inflation_rate/100) ** year)
        inflation_adjusted_savings.append(inflation_adjusted)
        
        # Calculate retirement income needed in future dollars
        future_income_needed = desired_income * ((1 + inflation_rate/100) ** year)
        retirement_income_needed.append(future_income_needed)
    
    # Calculate retirement phase
    retirement_savings = savings_balance
    annual_retirement_income = pension_income + social_security
    shortfall = retirement_income_needed[-1] - annual_retirement_income
    
    # Calculate if savings will last through retirement
    savings_last = True
    retirement_years = []
    retirement_ages = []
    retirement_savings_balance = []
    retirement_withdrawals = []
    
    for year in range(retirement_duration + 1):
        retirement_year = year
        age = retirement_age + year
        retirement_years.append(retirement_year)
        retirement_ages.append(age)
        
        if year == 0:
            balance = retirement_savings
            withdrawal = 0
        else:
            # Calculate investment growth
            investment_growth = balance * (annual_return / 100)
            
            # Withdraw shortfall amount
            withdrawal = shortfall
            balance -= withdrawal
            balance += investment_growth
            
            # Check if savings are depleted
            if balance < 0:
                balance = 0
                savings_last = False
        
        retirement_savings_balance.append(balance)
        retirement_withdrawals.append(withdrawal)
    
    # Create results dictionary
    results = {
        'years': years,
        'ages': ages,
        'savings': savings,
        'contributions': contributions,
        'growth': growth,
        'inflation_adjusted_savings': inflation_adjusted_savings,
        'retirement_income_needed': retirement_income_needed,
        'retirement_years': retirement_years,
        'retirement_ages': retirement_ages,
        'retirement_savings_balance': retirement_savings_balance,
        'retirement_withdrawals': retirement_withdrawals,
        'retirement_savings': retirement_savings,
        'shortfall': shortfall,
        'savings_last': savings_last,
        'retirement_duration': retirement_duration
    }
    
    return results

# Display results if calculate button is clicked
if calculate:
    # Calculate retirement plan
    results = calculate_retirement(
        current_age, retirement_age, life_expectancy, current_savings,
        annual_contribution, annual_return, inflation_rate, desired_income,
        pension_income, social_security
    )
    
    # Display summary
    st.markdown('<div class="highlight">', unsafe_allow_html=True)
    st.markdown(f'<h2 class="sub-header">Retirement Plan Summary</h2>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Years Until Retirement", f"{retirement_age - current_age}")
        st.metric("Projected Retirement Savings", f"${results['retirement_savings']:,.0f}")
    
    with col2:
        st.metric("Annual Shortfall in Retirement", f"${results['shortfall']:,.0f}")
        st.metric("Retirement Duration", f"{results['retirement_duration']} years")
    
    with col3:
        status = "✅ Sufficient" if results['savings_last'] else "❌ Insufficient"
        st.metric("Savings Status", status)
        st.metric("Monthly Shortfall in Retirement", f"${results['shortfall']/12:,.0f}")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Create tabs for different visualizations
    tab1, tab2, tab3 = st.tabs(["Savings Growth", "Retirement Projection", "Detailed Analysis"])
    
    with tab1:
        # Create savings growth chart
        st.subheader("Savings Growth Until Retirement")
        
        df_savings = pd.DataFrame({
            'Age': results['ages'],
            'Savings': results['savings'],
            'Inflation Adjusted Savings': results['inflation_adjusted_savings'],
            'Annual Contribution': results['contributions'],
            'Investment Growth': results['growth']
        })
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df_savings['Age'], y=df_savings['Savings'], 
                                mode='lines', name='Projected Savings', line=dict(width=3)))
        fig.add_trace(go.Scatter(x=df_savings['Age'], y=df_savings['Inflation Adjusted Savings'], 
                                mode='lines', name='Inflation-Adjusted Savings', line=dict(width=3)))
        
        fig.update_layout(
            title='Retirement Savings Growth',
            xaxis_title='Age',
            yaxis_title='Amount ($)',
            hovermode='x unified',
            height=500
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        # Create retirement projection chart
        st.subheader("Retirement Savings Projection")
        
        df_retirement = pd.DataFrame({
            'Age': results['retirement_ages'],
            'Savings Balance': results['retirement_savings_balance'],
            'Annual Withdrawal': results['retirement_withdrawals']
        })
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df_retirement['Age'], y=df_retirement['Savings Balance'], 
                                mode='lines', name='Savings Balance', line=dict(width=3)))
        
        fig.update_layout(
            title='Retirement Savings Balance',
            xaxis_title='Age',
            yaxis_title='Amount ($)',
            hovermode='x unified',
            height=500
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Display warning if savings are insufficient
        if not results['savings_last']:
            st.error("**Warning**: Your savings may not last through your retirement. Consider increasing your contributions, working longer, or adjusting your retirement income expectations.")
    
    with tab3:
        # Detailed analysis
        st.subheader("Detailed Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("##### Pre-Retirement Projection")
            df_pre = pd.DataFrame({
                'Age': results['ages'],
                'Savings': results['savings'],
                'Contributions': results['contributions'],
                'Investment Growth': results['growth']
            })
            df_pre['Savings'] = df_pre['Savings'].apply(lambda x: f"${x:,.0f}")
            df_pre['Contributions'] = df_pre['Contributions'].apply(lambda x: f"${x:,.0f}")
            df_pre['Investment Growth'] = df_pre['Investment Growth'].apply(lambda x: f"${x:,.0f}")
            st.dataframe(df_pre.set_index('Age'), use_container_width=True)
        
        with col2:
            st.markdown("##### Post-Retirement Projection")
            df_post = pd.DataFrame({
                'Age': results['retirement_ages'],
                'Savings Balance': results['retirement_savings_balance'],
                'Annual Withdrawal': results['retirement_withdrawals']
            })
            df_post['Savings Balance'] = df_post['Savings Balance'].apply(lambda x: f"${x:,.0f}")
            df_post['Annual Withdrawal'] = df_post['Annual Withdrawal'].apply(lambda x: f"${x:,.0f}")
            st.dataframe(df_post.set_index('Age'), use_container_width=True)
    
    # Recommendations section
    st.markdown("---")
    st.markdown('<h2 class="sub-header">Recommendations</h2>', unsafe_allow_html=True)
    
    if results['savings_last']:
        st.success("""
        - Your current plan appears to be on track for retirement
        - Continue with your current savings strategy
        - Consider periodically reviewing your plan as your circumstances change
        """)
    else:
        st.warning("""
        - **Increase your savings rate**: Try to save more each year
        - **Consider working longer**: Delaying retirement by a few years can significantly improve your financial security
        - **Adjust your retirement expectations**: You may need to reduce your desired retirement income
        - **Review your investment strategy**: Ensure your portfolio is appropriately allocated for your age and risk tolerance
        - **Consider additional income sources**: Part-time work during retirement could help bridge the gap
        """)
    
else:
    # Show instructions before calculation
    st.info("""
    ### How to Use This Calculator
    1. Adjust the input parameters in the sidebar to match your situation
    2. Click the 'Calculate Retirement Plan' button to see your personalized results
    3. Explore the different tabs to see detailed projections and analysis
    4. Use the recommendations to improve your retirement plan
    """)
    
    # Placeholder for demonstration
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Why Plan for Retirement?")
        st.write("""
        - Retirement can last 20-30 years or more
        - Social Security may not provide enough income
        - Healthcare costs tend to increase with age
        - Inflation erodes purchasing power over time
        - Starting early gives your investments more time to grow
        """)
    
    with col2:
        st.subheader("Key Retirement Planning Tips")
        st.write("""
        - Start saving as early as possible
        - Take advantage of employer matching contributions
        - Diversify your investments
        - Regularly review and adjust your plan
        - Consider working with a financial advisor
        """)
    
    # Sample chart placeholder
    st.subheader("The Power of Compound Interest")
    
    # Sample data for demonstration
    years = list(range(65))
    savings_early = [10000 * (1.07)**y for y in years]
    savings_late = [0] * 25 + [10000 * (1.07)**(y-25) for y in range(25, 65)]
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=years, y=savings_early, mode='lines', name='Starting at 25', line=dict(width=3)))
    fig.add_trace(go.Scatter(x=years, y=savings_late, mode='lines', name='Starting at 50', line=dict(width=3)))
    
    fig.update_layout(
        title='Impact of Starting Early (Assuming $10,000 annual contribution, 7% return)',
        xaxis_title='Age',
        yaxis_title='Savings Balance ($)',
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)

# Footer
st.markdown("---")
st.markdown("<p style='text-align: center; color: gray;'>This retirement calculator is for educational purposes only. Actual results may vary based on market conditions and personal circumstances.</p>", unsafe_allow_html=True)
