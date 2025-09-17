import React from "react";
import "./ContributionCalendar.css";

// Generate mock data: 53 weeks x 7 days
const weeks = 53;
const days = 7;
const levels = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"];

function getRandomLevel() {
    // 0-4, weighted for more zeros
    const weights = [0.5, 0.2, 0.15, 0.1, 0.05];
    let r = Math.random();
    let sum = 0;
    for (let i = 0; i < weights.length; i++) {
        sum += weights[i];
        if (r < sum) return i;
    }
    return 0;
}

const mockData: number[][] = Array.from({ length: weeks }, () =>
    Array.from({ length: days }, getRandomLevel)
);


// Month labels spaced to match GitHub's grid
const months = ["Sep", "Oct", "Nov", "Dec", "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep"];

// Only show Mon, Wed, Fri, aligned with grid rows
const weekdayLabels = ["", "Mon", "", "Wed", "", "Fri", ""];

export default function ContributionCalendar() {
    return (
        <div className="calendar-container">
            <div className="calendar-header">
                <span className="calendar-title">473 games played in the last year</span>
            </div>
            <div className="calendar-graph">
                <div className="calendar-months">
                    {months.map((m, i) => (
                        <span key={i} className="calendar-month">{m}</span>
                    ))}
                </div>
                <div className="calendar-grid">
                    {/* Day labels, aligned with rows */}
                    <div className="calendar-days">
                        {weekdayLabels.map((label, i) => (
                            <span key={i} className={label ? "calendar-day-label" : "calendar-day-label-empty"}>{label}</span>
                        ))}
                    </div>
                    {/* Contribution squares */}
                    <div className="calendar-weeks">
                        {mockData.map((week, wi) => (
                            <div key={wi} className="calendar-week">
                                {week.map((level, di) => (
                                    <div
                                        key={di}
                                        className="calendar-day"
                                        style={{ background: levels[level] }}
                                        title={`Contributions: ${level}`}
                                    ></div>
                                ))}
                            </div>
                        ))}
                    </div>
                </div>
            </div>
            <div className="calendar-footer">
                <div className="calendar-legend">
                    <span>Less</span>
                    {levels.map((color, i) => (
                        <span
                            key={i}
                            className="calendar-legend-square"
                            style={{ background: color }}
                        ></span>
                    ))}
                    <span>More</span>
                </div>
            </div>
        </div>
    );
}
