//
//  matrix.h
//  test
//
//  Created by Mengmeng  Wang on 5/12/21.
//

#ifndef matrix_h
#define matrix_h
#include "iostream"
using namespace std;

class matrix
{
private:
    int row_num, col_num;
    double **p;
    void initialize()
    {
        p=new double*[row_num];
        for(int i=0;i<row_num;i++)
        {
            p[i] = new double[col_num];
        }
    }
public:
    matrix(int rows,int cols)
    {
        row_num = rows;
        col_num = cols;
        initialize();
//        for (int i=1; i<row_num; i++)
//        {
//            for (int j=0; j<col_num; j++) {
//                p[i][j] = 0;
//            }
//        }
    }
    ~matrix()
    {
        for(int i=0;i<row_num;i++)
        {
            delete[] p[i];
        }
        delete[] p;
    }
    
    matrix& operator=(double * a)
    {
        for (int i=0; i<row_num; i++)
        {
            for (int j=0; j<col_num; j++)
            p[i][j]=*(a+i*col_num+j);
        }
        return *this;
    }
    
    matrix& operator+=(const matrix& m)
    {
        for (int i=0; i<row_num; i++)
        {
            for (int j=0; j<col_num; j++)
            p[i][j] += m.p[i][j];
        }
        return *this;
    }
    void show() const
    {
        for (int i=0; i<row_num; i++)
        {
            for (int j=0; j<col_num; j++)
            cout<<p[i][j]<<" ";
            cout<<endl;
            
        }
        cout<<endl;
    }
};

#endif /* matrix_h */
